import React from 'react';
import { useChat } from '../../context/ChatContext';
import { Trash2, Sparkles, Eye, EyeOff, Menu, PanelLeft } from 'lucide-react';

export function ChatHeader({ toggleSidebar }) {
  const { clearHistory, showDebugSources, setShowDebugSources } = useChat();

  return (
    <header className="h-14 border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between bg-white/90 backdrop-blur-md sticky top-0 z-20 flex-shrink-0 select-none">
      
      {/* Left side: Model / Persona selector & Sidebar Toggle */}
      <div className="flex items-center space-x-3">
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors md:hidden"
          title="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-slate-100/80 border border-slate-200/60 hover:bg-slate-100 cursor-default transition-colors">
            <Sparkles className="w-4 h-4 text-emerald-600 fill-emerald-600/20" />
            <span className="font-semibold text-slate-900 text-sm tracking-tight">
              Vishal's AI
            </span>
            <span className="text-[10px] bg-emerald-100 text-emerald-700 font-bold px-1.5 py-0.5 rounded-md">
              Digital Twin
            </span>
          </div>
        </div>
      </div>

      {/* Right side: Actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setShowDebugSources(!showDebugSources)}
          title={showDebugSources ? "Hide RAG Sources" : "Show RAG Sources"}
          className={`p-2 rounded-xl text-xs border transition-colors flex items-center ${
            showDebugSources 
              ? 'bg-blue-50 text-blue-700 border-blue-200' 
              : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
        >
          {showDebugSources ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>

        <button
          onClick={clearHistory}
          className="px-3 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-xl text-xs font-medium transition-colors flex items-center space-x-1.5 shadow-2xs"
          title="Clear Chat History"
        >
          <Trash2 className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Clear Chat</span>
        </button>
      </div>
    </header>
  );
}
