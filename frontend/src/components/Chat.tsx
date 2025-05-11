import React, { useEffect, useRef, useState } from 'react';
import { Message as MessageType } from '../types/chat';
import Message from './Message';
import ChatInput from './ChatInput';

const SESSION_STORAGE_KEY = 'news_chat_session_id';
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
        setSessionId(sessionId);
      } else {
        createNewSession();
      }
    } catch (error) {
      console.error('Error loading session:', error);
      createNewSession();
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Session creation response:', data);
        const newSessionId = typeof data === 'string'
          ? data
          : data.session_id || data.id || data.sessionId;
        if (!newSessionId) {
          console.error('No session ID found in response:', data);
          return;
        }
        localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
        setSessionId(newSessionId);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  useEffect(() => {
    const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
    if (storedSessionId) {
      loadSession(storedSessionId);
    } else {
      createNewSession();
    }
  }, []);

  const fetchMessages = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    let currentSessionId = sessionId;
    setIsLoading(true);

    // If no sessionId, create one first
    if (!currentSessionId) {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
          method: 'POST',
        });
        if (response.ok) {
          const data = await response.json();
          currentSessionId = typeof data === 'string'
            ? data
            : data.session_id || data.id || data.sessionId;
          if (!currentSessionId) {
            console.error('No session ID found in response:', data);
            setIsLoading(false);
            return;
          }
          localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId);
          setSessionId(currentSessionId);
        } else {
          setIsLoading(false);
          return;
        }
      } catch (error) {
        console.error('Error creating session:', error);
        setIsLoading(false);
        return;
      }
    }

    // Add user message immediately
    const userMessage: MessageType = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      await fetch(`${API_BASE_URL}/chat/sessions/${currentSessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, role: 'user' }),
      });
      // Fetch updated messages
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${currentSessionId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (!sessionId) return;
    try {
      await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      localStorage.removeItem(SESSION_STORAGE_KEY);
      createNewSession();
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-dark-900">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-primary-500 to-accent-500 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold">Welcome to News Chat</h2>
            <p className="text-center max-w-md">Ask me anything about the latest news and I'll help you stay informed.</p>
          </div>
        ) : (
          messages.map((message) => (
            <Message key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t border-dark-700 p-4 bg-dark-800">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
      {messages.length > 0 && (
        <button
          onClick={handleClearChat}
          className="absolute top-4 right-4 px-4 py-2 text-sm text-gray-400 hover:text-white bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors duration-200"
        >
          Clear Chat
        </button>
      )}
    </div>
  );
};

export default Chat; 