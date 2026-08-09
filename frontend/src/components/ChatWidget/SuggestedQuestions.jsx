import React from 'react';
import { useSuggestions } from '../../hooks/useSuggestions';
import { useChat } from '../../context/ChatContext';
import { Lightbulb, ChevronRight } from 'lucide-react';

export function SuggestedQuestions() {
  const { suggestions } = useSuggestions();
  const { sendMessage, isStreaming } = useChat();

  const questionsList = [
    "Tell me about your projects",
    "What are your technical skills?",
    "Explain your AI experience",
    "What technologies do you work with?",
    "What roles are you looking for?",
    "How can I contact you?"
  ];

  const displayQuestions = (suggestions && suggestions.length >= 4) ? suggestions : questionsList;

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs space-y-2.5">
      <div className="flex items-center space-x-2 text-slate-900 font-bold text-xs">
        <Lightbulb className="w-3.5 h-3.5 text-amber-500 fill-amber-500/20" />
        <span>Suggested Questions</span>
      </div>

      <div className="space-y-1.5">
        {displayQuestions.slice(0, 5).map((q, idx) => (
          <button
            key={idx}
            disabled={isStreaming}
            onClick={() => sendMessage(q)}
            className="w-full text-left text-xs bg-white hover:bg-slate-50 text-slate-700 font-medium border border-slate-200 hover:border-blue-300 rounded-xl px-3 py-2 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs"
          >
            <span className="truncate pr-2">{q}</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 transition-colors flex-shrink-0" />
          </button>
        ))}
      </div>
    </div>
  );
}
