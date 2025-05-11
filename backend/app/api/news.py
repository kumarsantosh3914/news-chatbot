from fastapi import APIRouter, HTTPException
from app.rag.ingestion import news_service

router = APIRouter()

@router.post("/ingest")
async def ingest_news():
    """Ingest news articles from various sources."""
    try:
        await news_service.ingest_news()
        return {"message": "News ingestion completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 