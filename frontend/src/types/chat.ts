export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface MessageResponse {
  messages: Message[];
}

export interface ChatSession {
  id: string;
  messages: Message[];
}

export interface MessageCreate {
  content: string;
  role: 'user' | 'assistant';
} 