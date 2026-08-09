import React, { useState } from 'react';
import { Avatar } from '../Common/Avatar';
import { Badge } from '../Common/Badge';
import { useChat } from '../../context/ChatContext';
import { Copy, Check, Database, ChevronDown, ChevronUp, FileDown } from 'lucide-react';

export function MessageItem({ message, isStreamingActive = false }) {
  const [copied, setCopied] = useState(false);
  const [showSourcesDetails, setShowSourcesDetails] = useState(true);
  const { showDebugSources } = useChat();

  const isUser = message.role === 'user';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Format assistant message content with clean bullet points and section highlights
  const renderFormattedContent = (content) => {
    if (!content) return null;

    return content.split('\n').map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const bulletText = trimmed.substring(2);
        return (
          <div key={idx} className="flex items-start space-x-2 my-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-2 flex-shrink-0"></span>
            <span className="text-slate-800">{bulletText}</span>
          </div>
        );
      }
      if (trimmed.endsWith(':') && trimmed.length < 50 && !trimmed.includes('.')) {
        return <div key={idx} className="font-semibold text-slate-900 mt-3 mb-1">{trimmed}</div>;
      }
      return <div key={idx} className={trimmed === '' ? 'h-2' : 'my-0.5 text-slate-800'}>{line}</div>;
    });
  };

  return (
    <div className={`flex space-x-3 sm:space-x-4 my-6 animate-slide-up ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <Avatar size="sm" isUser={isUser} />

      <div className={`flex flex-col max-w-[88%] sm:max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        
        {/* Message Bubble Container */}
        <div
          className={`relative group text-sm leading-relaxed ${
            isUser
              ? 'bg-blue-600 text-white rounded-3xl rounded-tr-sm px-4.5 py-3 shadow-2xs'
              : 'bg-white border border-slate-200/80 text-slate-800 rounded-3xl rounded-tl-sm px-5 py-4 shadow-2xs'
          }`}
        >
          <div className="whitespace-pre-wrap font-sans text-[14px]">
            {isUser ? message.content : renderFormattedContent(message.content)}
            {isStreamingActive && (
              <span className="inline-block w-1.5 h-4 ml-1 bg-emerald-600 animate-pulse"></span>
            )}
          </div>

          {!isUser && !isStreamingActive && (
            <button
              onClick={copyToClipboard}
              className="absolute top-2 right-2 p-1.5 text-slate-400 opacity-0 group-hover:opacity-100 hover:text-slate-700 bg-slate-100 rounded-lg transition-all"
              title="Copy response"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Resume PDF Card — shown only for RESUME_REQUEST intent */}
        {!isUser && message.resume_data && (
          <div className="mt-2.5 w-full bg-white border border-slate-200/80 rounded-2xl p-3.5 shadow-2xs animate-fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0">
                  <FileDown className="w-4.5 h-4.5 text-blue-600" />
                </div>
                <div>
                  <p className="text-[12.5px] font-semibold text-slate-900 leading-tight">Vishal Kumar — Resume</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">{message.resume_data.file_name}</p>
                </div>
              </div>
              <a
                href={message.resume_data.download_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-[11.5px] font-semibold rounded-xl transition-colors shadow-sm"
              >
                <FileDown className="w-3.5 h-3.5" />
                <span>Download</span>
              </a>
            </div>
          </div>
        )}

        {/* Sources Box for RAG Grounded Assistant Messages */}
        {!isUser && (message.sources?.length > 0 || message.collections?.length > 0) && (
          <div className="mt-2.5 w-full bg-slate-50 border border-slate-200/80 rounded-2xl p-3 text-xs text-slate-600 space-y-2 animate-fade-in">
            <button
              onClick={() => setShowSourcesDetails(!showSourcesDetails)}
              className="w-full flex items-center justify-between font-medium text-slate-700 hover:text-blue-600 transition-colors"
            >
              <div className="flex items-center space-x-1.5">
                <Database className="w-3.5 h-3.5 text-emerald-600" />
                <span className="font-semibold text-[11.5px] text-slate-800">Retrieved Grounding Sources</span>
              </div>
              <div className="flex items-center space-x-1 text-[11px] text-slate-400">
                <span>{message.sources?.length || 0} sources</span>
                {showSourcesDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </div>
            </button>

            {showSourcesDetails && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {message.sources ? (
                  message.sources.map((s, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[11px] text-slate-700 shadow-2xs"
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${idx % 2 === 0 ? 'bg-blue-500' : 'bg-emerald-500'}`}></span>
                      <span>{s.collection}/{s.source}.md</span>
                    </span>
                  ))
                ) : (
                  message.collections?.map((col, i) => (
                    <Badge key={i} variant="indigo">{col}</Badge>
                  ))
                )}
              </div>
            )}

            {/* Debug Snippets View */}
            {showDebugSources && showSourcesDetails && message.sources && (
              <div className="space-y-1.5 pt-2 border-t border-slate-200/60">
                {message.sources.map((s, idx) => (
                  <div key={idx} className="bg-white p-2.5 rounded-xl border border-slate-200/80 text-[10.5px]">
                    <div className="flex justify-between font-mono font-medium text-slate-700">
                      <span>{s.collection}</span>
                      <span className="text-slate-400">{s.source}</span>
                    </div>
                    <p className="text-slate-500 italic mt-0.5 truncate">{s.content_snippet}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
