import React, { useEffect, useRef } from 'react';
import { useChat } from '../../context/ChatContext';
import { MessageItem } from './MessageItem';
import { LoadingDots } from '../Common/LoadingDots';
import { Avatar } from '../Common/Avatar';

export function MessageList() {
  const { messages, isStreaming, currentStreamedText, activeMetadata } = useChat();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamedText, isStreaming]);

  return (
    <div className="flex-1 overflow-y-auto w-full">
      <div className="max-w-3xl xl:max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-2">
        {messages.map((msg, index) => (
          <MessageItem key={index} message={msg} />
        ))}

        {isStreaming && (
          <div className="animate-fade-in">
            {currentStreamedText ? (
              <MessageItem
                message={{
                  role: 'assistant',
                  content: currentStreamedText,
                  intent: activeMetadata?.intent,
                  collections: activeMetadata?.collections,
                  sources: activeMetadata?.sources
                }}
                isStreamingActive={true}
              />
            ) : (
              <div className="flex space-x-3 my-4">
                <Avatar size="sm" isUser={false} />
                <div className="bg-white border border-slate-200/80 rounded-2xl rounded-tl-none px-4 py-3 flex items-center space-x-2 shadow-2xs">
                  <span className="text-xs text-slate-500 font-medium">Searching knowledge base...</span>
                  <LoadingDots />
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
