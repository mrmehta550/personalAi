import React from 'react';
import { Bot, User, Sparkles } from 'lucide-react';

export function Avatar({ size = "md", isUser = false }) {
  const sizeClasses = {
    sm: "w-7 h-7 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-9 h-9 text-base"
  };

  if (isUser) {
    return (
      <div className={`${sizeClasses[size]} rounded-full bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 font-semibold shadow-2xs`}>
        <User className="w-4 h-4" />
      </div>
    );
  }

  return (
    <div className={`${sizeClasses[size]} rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold flex-shrink-0 shadow-2xs`}>
      <Sparkles className="w-4 h-4 fill-white" />
    </div>
  );
}
