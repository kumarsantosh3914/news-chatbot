import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store

# Configure logging
logger = logging.getLogger(__name__)


class Article:
    """Class representing a news article."""
    
    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        published_date: Optional[datetime] = None,
        source: Optional[str] = None
    ):
        self.title = title
        self.content = content
        self.url = url
        self.published_date = published_date
        self.source = source


class TextChunk:
    """Class representing a chunk of text from an article."""
    
    def __init__(
        self,
        text: str,
        article_url: str,
        article_title: str,
        source: Optional[str] = None,
        published_date: Optional[datetime] = None
    ):
        self.text = text
        self.article_url = article_url
        self.article_title = article_title
        self.source = source
        self.published_date = published_date
    
    def get_meta(self) -> Dict:
        """Get meta for the chunk."""
        return {
            "article_url": self.article_url,
            "article_title": self.article_title,
            "source": self.source,
            "published_date": self.published_date.isoformat() if self.published_date else None,
        }


class NewsIngestionService:
    """Service for ingesting news articles using web scraping."""
    
    def __init__(self):
        """Initialize the news ingestion service."""
        # List of news sources to crawl
        self.news_sources = [
            "https://www.reuters.com/world/",
            "https://www.bbc.com/news/world",
            "https://www.theguardian.com/world",
            "https://www.aljazeera.com/news/",
            "https://www.dw.com/en/top-stories/s-9097",
            "https://www.france24.com/en/",
            "https://www.thehindu.com/news/international/",
            "https://www.ndtv.com/world-news"
        ]
        
        # Headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Rate limiting
        self.min_delay = 2  # Minimum delay between requests in seconds
        self.last_request_time = 0
    
    async def ingest_news(self):
        """Process news using web scraping."""
        all_articles = []
        
        for source in self.news_sources:
            try:
                logger.info(f"Fetching news from {source}")
                # Rate limiting
                self._wait_for_rate_limit()
                
                # Get the main page
                response = requests.get(source, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links (this will need to be customized per site)
                article_links = self._find_article_links(soup, source)
                logger.info(f"Found {len(article_links)} article links on {source}")
                
                # Process each article
                for link in article_links[:5]:  # Limit to 5 articles per source
                    try:
                        # Rate limiting
                        self._wait_for_rate_limit()
                        
                        article = await self._process_article(link)
                        if article:
                            all_articles.append(article)
                            logger.info(f"Successfully fetched article: {article.title}")
                    except Exception as e:
                        logger.error(f"Error processing article {link}: {e}")
                        continue
                    
            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                continue
        
        if not all_articles:
            logger.warning("No articles were successfully processed.")
            return
        
        logger.info(f"Processing {len(all_articles)} articles into chunks")
        # Process articles into chunks
        all_chunks = []
        for article in all_articles:
            chunks = self._chunk_article(article)
            all_chunks.extend(chunks)
        
        logger.info(f"Generated {len(all_chunks)} chunks from {len(all_articles)} articles")
        
        # Generate embeddings and store in vector database
        texts = [chunk.text for chunk in all_chunks]
        metas = [chunk.get_meta() for chunk in all_chunks]
        
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = embedding_service.generate_embeddings(texts)
        
        logger.info(f"Storing {len(embeddings)} embeddings in vector database")
        vector_store.store(texts, embeddings, metas)
        
        logger.info(f"Successfully ingested {len(texts)} chunks from {len(all_articles)} articles")
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_delay:
            time.sleep(self.min_delay - time_since_last_request)
        self.last_request_time = time.time()
    
    def _find_article_links(self, soup: BeautifulSoup, source: str) -> List[str]:
        """Find article links in the page."""
        links = []
        
        # Common patterns for article links
        if "reuters.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/article/' in a['href']]
        elif "bbc.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/news/' in a['href']]
        elif "theguardian.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/article/' in a['href']]
        elif "aljazeera.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/news/' in a['href']]
        elif "dw.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/en/' in a['href']]
        elif "france24.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/en/' in a['href']]
        elif "thehindu.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/news/international/' in a['href']]
        elif "ndtv.com" in source:
            links = [a['href'] for a in soup.find_all('a', href=True) if '/world-news/' in a['href']]
        
        # Make sure links are absolute
        links = [link if link.startswith('http') else f"{source.rstrip('/')}/{link.lstrip('/')}" for link in links]
        return list(set(links))  # Remove duplicates
    
    async def _process_article(self, url: str) -> Optional[Article]:
        """Process a single article."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            if not title:
                return None
            title = title.get_text().strip()
            
            # Extract content
            content = ""
            article_body = soup.find('article') or soup.find('main') or soup.find('div', class_='article-body')
            if article_body:
                # Remove unwanted elements
                for element in article_body.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    element.decompose()
                
                # Get text from paragraphs
                paragraphs = article_body.find_all('p')
                content = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            
            if not content:
                return None
            
            # Extract date if available
            date = None
            date_element = soup.find('time') or soup.find('meta', property='article:published_time')
            if date_element:
                date_str = date_element.get('datetime') or date_element.get('content')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
            
            return Article(
                title=title,
                content=content,
                url=url,
                published_date=date,
                source=url.split('/')[2]  # Extract domain as source
            )
            
        except Exception as e:
            logger.error(f"Error processing article {url}: {e}")
            return None
    
    def _chunk_article(self, article: Article) -> List[TextChunk]:
        """Split an article into optimal chunks for embedding."""
        # Simple chunking strategy: split by paragraphs then combine to target size
        
        # First, split content by paragraphs
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', article.content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Add title as the first chunk
        title_chunk = TextChunk(
            text=f"Title: {article.title}",
            article_url=article.url,
            article_title=article.title,
            source=article.source,
            published_date=article.published_date
        )
        
        # Create chunks with target size of ~200-300 words
        target_size = 250
        chunks = [title_chunk]
        current_chunk = ""
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph_words = len(paragraph.split())
            
            if current_size + paragraph_words > target_size and current_chunk:
                # Current chunk is full, save it and start a new one
                chunks.append(TextChunk(
                    text=current_chunk,
                    article_url=article.url,
                    article_title=article.title,
                    source=article.source,
                    published_date=article.published_date
                ))
                current_chunk = paragraph
                current_size = paragraph_words
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += " " + paragraph
                else:
                    current_chunk = paragraph
                current_size += paragraph_words
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(TextChunk(
                text=current_chunk,
                article_url=article.url,
                article_title=article.title,
                source=article.source,
                published_date=article.published_date
            ))
        
        return chunks


# Singleton instance
news_service = NewsIngestionService()