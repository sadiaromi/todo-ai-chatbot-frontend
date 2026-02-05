'use client';

import { Suspense } from 'react';
import ChatInterface from './ChatInterface';

const LoadingSpinner = () => (
  <div className="chat-container">
    <div className="messages">
      {/* Show a loading state until client mounts */}
      <div className="message assistant-message">
        <div className="message-content">
          Loading chat interface...
        </div>
        <div className="message-role">
          AI Assistant
        </div>
      </div>
    </div>
    <div className="input-form">
      <input
        value=""
        placeholder="Type your message here..."
        disabled={true}
        className="message-input"
      />
      <button type="button" disabled={true} className="send-button">
        Send
      </button>
    </div>
  </div>
);

const ClientChatInterface = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <ChatInterface />
    </Suspense>
  );
};

export default ClientChatInterface;