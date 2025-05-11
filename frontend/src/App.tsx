import React from 'react';
import Chat from './components/Chat';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-dark-900 text-gray-100">
      <div className="max-w-7xl mx-auto">
        <Chat />
      </div>
    </div>
  );
};

export default App; 