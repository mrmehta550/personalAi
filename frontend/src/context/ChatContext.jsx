import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchChatHistory, clearChatHistory } from '../services/api';
import { useChatStream } from '../hooks/useChatStream';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [threadId, setThreadId] = useState(() => {
    return localStorage.getItem('personal_ai_thread_id') || `session_${Math.random().toString(36).substring(2, 9)}`;
  });

  const [messages, setMessages] = useState([]);
  const [showDebugSources, setShowDebugSources] = useState(false);
  const { isStreaming, currentStreamedText, activeMetadata, streamMessage, stopStreaming } = useChatStream();

  useEffect(() => {
    localStorage.setItem('personal_ai_thread_id', threadId);
    fetchChatHistory(threadId).then(history => {
      if (history && history.length > 0) {
        setMessages(history);
      } else {
        // Initial welcome message from AI digital twin
        setMessages([
          {
            role: 'assistant',
            content: "Hello! I am the AI assistant representing Vishal Kumar's professional portfolio. Ask about my background, projects, technical skills, experience, or how to get in touch!",
            timestamp: new Date().toISOString()
          }
        ]);
      }
    });
  }, [threadId]);

  const sendMessage = async (text) => {
    if (!text.trim() || isStreaming) return;

    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    await streamMessage({
      threadId,
      message: text,
      onComplete: ({ text: responseText, metadata }) => {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: responseText,
            intent: metadata?.intent,
            collections: metadata?.collections,
            sources: metadata?.sources,
            resume_data: metadata?.resume_data || null,  // PDF card data for RESUME_REQUEST
            timestamp: new Date().toISOString()
          }
        ]);
      },
      onError: (err) => {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: "I encountered an error connecting to my backend vector memory service. Please try again in a moment!",
            isError: true,
            timestamp: new Date().toISOString()
          }
        ]);
      }
    });
  };

  const handleClearHistory = async () => {
    await clearChatHistory(threadId);
    setMessages([
      {
        role: 'assistant',
        content: "Chat history cleared. How can I assist you with my portfolio today?",
        timestamp: new Date().toISOString()
      }
    ]);
  };

  const exportHistory = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(messages, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `chat_export_${threadId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <ChatContext.Provider
      value={{
        threadId,
        messages,
        isStreaming,
        currentStreamedText,
        activeMetadata,
        showDebugSources,
        setShowDebugSources,
        sendMessage,
        stopStreaming,
        clearHistory: handleClearHistory,
        exportHistory
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  return useContext(ChatContext);
}
