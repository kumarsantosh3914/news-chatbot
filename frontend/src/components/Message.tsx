import React, { useEffect, useState } from 'react';
import { Message as MessageType } from '../types/chat';

interface MessageProps {
  message: MessageType;
  isStreaming?: boolean;
}

const Message: React.FC<MessageProps> = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user';
  const [displayedContent, setDisplayedContent] = useState(message.content);

  useEffect(() => {
    if (isStreaming) {
      setDisplayedContent(message.content);
    }
  }, [message.content, isStreaming]);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 group`}>
      <div
        className={`relative max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
            : 'bg-dark-800 text-gray-100 border border-dark-700'
        } shadow-lg transition-all duration-200 hover:shadow-xl`}
      >
        <div className="flex items-start space-x-3">
          {!isUser && (
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-gradient-to-r from-accent-500 to-accent-600 flex items-center justify-center ring-2 ring-dark-700">
                <span className="text-white text-xs font-medium">AI</span>
              </div>
            </div>
          )}
          <div className="flex-1">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{displayedContent}</p>
            <span className="text-xs opacity-70 mt-1 block">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
          {isUser && (
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-gradient-to-r from-dark-600 to-dark-700 flex items-center justify-center ring-2 ring-dark-700">
                <span className="text-white text-xs font-medium">You</span>
              </div>
            </div>
          )}
        </div>
        {isStreaming && (
          <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-500 to-transparent animate-gradient-x"></div>
        )}
      </div>
    </div>
  );
};

export default Message; 