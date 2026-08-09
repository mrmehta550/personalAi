import React, { useState } from 'react';
import { ChatProvider, useChat } from './context/ChatContext';
import { ChatContainer } from './components/ChatWidget/ChatContainer';
import { SuggestedQuestions } from './components/ChatWidget/SuggestedQuestions';
import { 
  Plus, 
  MessageSquare, 
  User, 
  Folder, 
  Code, 
  Briefcase, 
  GraduationCap, 
  Mail, 
  Sparkles, 
  Github, 
  Linkedin, 
  ShieldCheck, 
  X 
} from 'lucide-react';

function DashboardContent() {
  const { sendMessage, clearHistory } = useChat();
  const [activeTab, setActiveTab] = useState('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, query: null },
    { id: 'about', label: 'About Me', icon: User, query: 'Tell me about yourself.' },
    { id: 'projects', label: 'Projects', icon: Folder, query: 'Tell me about your projects' },
    { id: 'skills', label: 'Skills', icon: Code, query: 'What are your technical skills?' },
    { id: 'experience', label: 'Experience', icon: Briefcase, query: 'Tell me about your AI experience' },
    { id: 'education', label: 'Education', icon: GraduationCap, query: 'What is your educational background?' },
    { id: 'contact', label: 'Contact', icon: Mail, query: 'How can I contact you?' },
  ];

  const handleNavClick = (item) => {
    setActiveTab(item.id);
    setSidebarOpen(false);
    if (item.query) {
      sendMessage(item.query);
    }
  };

  const handleNewChat = () => {
    clearHistory();
    setActiveTab('chat');
    setSidebarOpen(false);
  };

  return (
    <div className="h-screen w-screen flex bg-slate-50 text-slate-900 overflow-hidden font-sans select-none">
      
      {/* Mobile backdrop overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-30 md:hidden"
        />
      )}

      {/* LEFT SIDEBAR (ChatGPT style) */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-64 xl:w-72 border-r border-slate-200/80 bg-slate-100/90 backdrop-blur-md flex flex-col justify-between p-3 flex-shrink-0 transition-transform duration-300 md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="space-y-3">
          
          {/* Top Bar: New Chat & Mobile Close */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleNewChat}
              className="flex-1 flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-800 text-xs font-semibold shadow-2xs transition-colors"
            >
              <div className="flex items-center space-x-2">
                <Plus className="w-4 h-4 text-blue-600" />
                <span>New Chat</span>
              </div>
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            </button>

            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 text-slate-400 hover:text-slate-700 md:hidden rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1 pt-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item)}
                  className={`w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-slate-200/80 text-slate-900 font-semibold shadow-2xs'
                      : 'text-slate-600 hover:bg-slate-200/50 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom User Profile Section */}
        <div className="pt-3 border-t border-slate-200/80 space-y-3">
          <div className="flex items-center space-x-3 px-2 py-1.5">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 font-bold text-white flex items-center justify-center text-xs shadow-xs flex-shrink-0">
              VK
            </div>
            <div className="truncate min-w-0">
              <h4 className="font-bold text-slate-900 text-xs truncate">Vishal Kumar</h4>
              <p className="text-[11px] text-slate-500 truncate">Python &amp; AI Developer</p>
            </div>
          </div>

          <div className="flex items-center justify-between px-2 text-[11px] text-slate-400">
            <div className="flex items-center space-x-2">
              <button onClick={() => sendMessage("Show me your GitHub profile.")} className="hover:text-slate-700 transition-colors" title="GitHub">
                <Github className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => sendMessage("Show me your LinkedIn profile.")} className="hover:text-slate-700 transition-colors" title="LinkedIn">
                <Linkedin className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => sendMessage("How can I contact you?")} className="hover:text-slate-700 transition-colors" title="Email Contact">
                <Mail className="w-3.5 h-3.5" />
              </button>
            </div>
            <span>© 2026</span>
          </div>
        </div>
      </aside>

      {/* CENTER MAIN CHAT AREA (ChatGPT style full height) */}
      <main className="flex-1 h-full flex flex-col relative bg-white overflow-hidden">
        <ChatContainer toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      </main>

      {/* RIGHT SIDEBAR PANEL (Collapsible / Sleek on larger screens) */}
      <aside className="hidden lg:flex w-72 xl:w-80 flex-shrink-0 border-l border-slate-200/80 bg-slate-50/50 p-4 flex-col justify-between space-y-4 overflow-y-auto">
        <div className="space-y-4">
          <SuggestedQuestions />

          {/* Let's Connect Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs space-y-2.5 text-xs">
            <h4 className="font-bold text-slate-900">Let's Connect</h4>
            <div className="space-y-2 text-slate-600">
              <button onClick={() => sendMessage("How can I contact you?")} className="w-full flex items-center space-x-2 hover:text-blue-600 transition-colors text-left group">
                <Mail className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600" />
                <span className="truncate">Direct Message / Contact Form</span>
              </button>
              <button onClick={() => sendMessage("Give me your LinkedIn profile.")} className="w-full flex items-center space-x-2 hover:text-blue-600 transition-colors text-left group">
                <Linkedin className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600" />
                <span className="truncate">LinkedIn Profile</span>
              </button>
              <button onClick={() => sendMessage("Show me your GitHub repositories.")} className="w-full flex items-center space-x-2 hover:text-blue-600 transition-colors text-left group">
                <Github className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600" />
                <span className="truncate">GitHub Repositories</span>
              </button>
            </div>
          </div>
        </div>

        {/* Privacy First Card */}
        <div className="bg-blue-50/70 border border-blue-100 rounded-2xl p-3.5 text-xs text-blue-900 space-y-1">
          <div className="flex items-center space-x-1.5 font-bold">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Privacy First</span>
          </div>
          <p className="text-[11px] text-blue-800/80 leading-relaxed">
            I only answer based on my portfolio knowledge base and do not share any personal or private information.
          </p>
        </div>
      </aside>

    </div>
  );
}

export default function App() {
  return (
    <ChatProvider>
      <DashboardContent />
    </ChatProvider>
  );
}
