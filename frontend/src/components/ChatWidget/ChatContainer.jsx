import React from 'react';
import { ChatHeader } from './ChatHeader';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';

export function ChatContainer({ toggleSidebar }) {
  return (
    <div className="h-full w-full flex flex-col relative bg-white overflow-hidden flex-1">
      <ChatHeader toggleSidebar={toggleSidebar} />
      <MessageList />
      <InputBox />
    </div>
  );
}
