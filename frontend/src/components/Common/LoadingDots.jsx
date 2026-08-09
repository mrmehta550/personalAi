import React from 'react';

export function LoadingDots() {
  return (
    <div className="flex items-center space-x-1.5 py-1 px-2">
      <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 rounded-full bg-brand-300 animate-bounce"></div>
    </div>
  );
}
