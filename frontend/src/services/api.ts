import axios from 'axios';
import { Message, MessageResponse } from '../types/chat';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  createSession: async (): Promise<string> => {
    const response = await api.post('/chat/sessions');
    const data = response.data;
    const newSessionId = typeof data === 'string'
      ? data
      : data.session_id || data.id || data.sessionId;
    console.log('Session creation response:', data);
    return newSessionId;
  },

  getSessionMessages: async (sessionId: string): Promise<MessageResponse> => {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`);
    return response.data;
  },

  sendMessage: async (sessionId: string, content: string): Promise<Message> => {
    const response = await api.post(`/chat/sessions/${sessionId}/messages`, {
      content,
      role: 'user'
    });
    return response.data;
  },

  clearSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/sessions/${sessionId}`);
  },

  createWebSocket: (sessionId: string, onMessage: (content: string) => void): WebSocket => {
    const ws = new WebSocket(`${API_BASE_URL}/chat/ws/${sessionId}`);
    
    ws.onmessage = (event) => {
      onMessage(event.data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }
};

export default api; 