'use client';

import { useState, useRef, useEffect } from 'react';
import { useSession } from '../lib/auth-react';
import apiService from '../services/api';

const ChatInterface = ({ onTaskUpdate }) => {
  const { data: session } = useSession();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => scrollToBottom(), [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);

    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      createdAt: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');

    try {
      const userId = session?.user?.id || 'demo-user';
      const lastMessage = messages[messages.length - 1];
      const conversationId = lastMessage?.conversationId || null;

      // Send message to Claude backend
      const response = await apiService.sendMessage(userId, currentInput, conversationId);

      // Show AI assistant message
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        content: response.response,
        role: 'assistant',
        createdAt: new Date().toISOString(),
        conversationId: response.conversation_id
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Handle tool calls automatically
      if (response.tool_calls && response.tool_calls.length > 0) {
        for (const call of response.tool_calls) {
          switch (call.name) {
            case 'add_task':
              // Access arguments from the call, not parameters
              const addArgs = call.arguments || call.parameters || {};
              await apiService.createTask(userId, {
                title: addArgs.title || addArgs.task_title || 'New Task',
                description: addArgs.description || '',
                priority: addArgs.priority || 'medium'
              });
              break;
            case 'update_task':
              const updateArgs = call.arguments || call.parameters || {};
              await apiService.updateTask(userId, updateArgs.task_id, {
                title: updateArgs.title,
                description: updateArgs.description,
                priority: updateArgs.priority,
                status: updateArgs.status
              });
              break;
            case 'complete_task':
              const completeArgs = call.arguments || call.parameters || {};
              await apiService.updateTask(userId, completeArgs.task_id, {
                ...completeArgs,
                status: 'completed'
              });
              break;
            case 'delete_task':
              const deleteArgs = call.arguments || call.parameters || {};
              await apiService.deleteTask(userId, deleteArgs.task_id);
              break;
          }
        }

        // Refresh tasks in Dashboard after a small delay
        if (onTaskUpdate) setTimeout(() => onTaskUpdate(), 500);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error processing your request.',
        role: 'assistant',
        createdAt: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container flex flex-col h-full">
      <div className="messages flex-1 overflow-y-auto p-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'} mb-2`}
          >
            <div className="message-content p-2 rounded bg-gray-100">{message.content}</div>
            <div className="message-role text-xs text-gray-500 mt-1">
              {message.role === 'user' ? 'You' : 'AI Assistant'}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant-message mb-2">
            <div className="message-content p-2 rounded bg-gray-100">Thinking...</div>
            <div className="message-role text-xs text-gray-500 mt-1">AI Assistant</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form flex p-4 border-t border-gray-200">
        <input
          value={input}
          placeholder="Type your message here..."
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="ml-2 px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
