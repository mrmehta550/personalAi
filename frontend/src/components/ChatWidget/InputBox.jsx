import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { Send, Square, Shield, Folder, Code, Sparkles, Briefcase } from 'lucide-react';

export function InputBox() {
  const [input, setInput] = useState('');
  const { sendMessage, isStreaming, stopStreaming } = useChat();
  const textareaRef = useRef(null);

  // Auto-grow textarea height like ChatGPT
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const quickPills = [
    { label: "My projects", query: "Tell me about your projects", icon: Folder },
    { label: "My skills", query: "What are your technical skills?", icon: Code },
    { label: "AI Mail Automation", query: "Tell me about your AI Mail Automation project.", icon: Sparkles },
    { label: "My experience", query: "Tell me about your AI experience", icon: Briefcase },
  ];

  return (
    <div className="sticky bottom-0 bg-gradient-to-t from-white via-white to-transparent pt-4 pb-3 px-4 sm:px-6 z-10 flex-shrink-0">
      <div className="max-w-3xl xl:max-w-4xl mx-auto w-full space-y-2.5">
        
        {/* Quick Suggestion Pills above input capsule */}
        {!isStreaming && (
          <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
            {quickPills.map((pill, idx) => {
              const Icon = pill.icon;
              return (
                <button
                  key={idx}
                  onClick={() => sendMessage(pill.query)}
                  className="inline-flex items-center space-x-1.5 text-xs bg-slate-100/80 hover:bg-slate-200/80 text-slate-700 font-medium border border-slate-200/80 rounded-full px-3 py-1.5 shadow-2xs transition-all active:scale-95"
                >
                  <Icon className="w-3.5 h-3.5 text-blue-600" />
                  <span>{pill.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* ChatGPT Style Rounded Input Box */}
        <form onSubmit={handleSubmit} className="relative bg-slate-100/90 focus-within:bg-white border border-slate-200/90 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 rounded-3xl p-2 pl-4 flex items-end shadow-sm transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message Vishal's AI..."
            rows={1}
            maxLength={1000}
            className="w-full text-slate-800 placeholder-slate-400 text-sm focus:outline-none resize-none bg-transparent max-h-40 py-1.5"
          />

          <div className="flex items-center space-x-2 flex-shrink-0 ml-2 mb-0.5">
            <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
              {input.length}/1000
            </span>

            {isStreaming ? (
              <button
                type="button"
                onClick={stopStreaming}
                className="p-2 bg-rose-600 hover:bg-rose-700 text-white rounded-full transition-all shadow-sm flex items-center justify-center"
                title="Stop Generation"
              >
                <Square className="w-4 h-4 fill-white" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim()}
                className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-all disabled:opacity-30 disabled:hover:bg-blue-600 shadow-md shadow-blue-500/20 active:scale-95 flex items-center justify-center"
                title="Send Message"
              >
                <Send className="w-4 h-4 fill-white" />
              </button>
            )}
          </div>
        </form>

        {/* ChatGPT Style Footer Disclaimer */}
        <div className="flex justify-center items-center text-[11px] text-slate-500 space-x-1.5 text-center px-2">
          <Shield className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
          <span>Answers are grounded in my portfolio knowledge. I don't share private or family information.</span>
        </div>

      </div>
    </div>
  );
}
