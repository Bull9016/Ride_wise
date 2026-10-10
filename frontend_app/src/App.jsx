import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [role, setRole] = useState('Customer');
  const [customerId, setCustomerId] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isLoggedIn) {
      fetchSessions();
    }
  }, [isLoggedIn, customerId]);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`http://localhost:8001/api/sessions${customerId ? `?customer_id=${customerId}` : ''}`);
      setSessions(res.data);
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  const loadSession = async (id) => {
    try {
      const res = await axios.get(`http://localhost:8001/api/sessions/${id}`);
      setSessionId(id);
      setMessages(res.data);
    } catch (e) {
      console.error("Failed to load session", e);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (role === 'Customer' && (!customerId.trim() || !mobileNumber.trim())) {
      alert("Please enter both your Customer ID and Mobile Number.");
      return;
    }
    setIsLoggedIn(true);
    setSessionId(crypto.randomUUID());
    setMessages([]);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setRole('Customer');
    setCustomerId('');
    setMobileNumber('');
    setMessages([]);
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(crypto.randomUUID());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const payload = {
        role: role,
        message: input,
        session_id: sessionId,
        mobile_number: role === 'Customer' ? mobileNumber : null,
        customer_id: role === 'Customer' ? customerId : null
      };

      const response = await axios.post('http://localhost:8001/api/chat', payload);
      
      setMessages((prev) => [...prev, { text: response.data.answer, sender: 'agent' }]);
    } catch (error) {
      if (error.response?.status === 401) {
        setMessages((prev) => [...prev, { text: "Error: " + error.response.data.detail, sender: 'error' }]);
      } else {
        setMessages((prev) => [...prev, { text: "Error: Could not connect to the backend.", sender: 'error' }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-[#0B1120] bg-gradient-to-br from-[#0B1120] via-[#111827] to-[#0F172A] flex items-center justify-center p-4 font-sans text-slate-100 relative overflow-hidden">
        {/* Decorative background blobs */}
        <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-pulse" style={{ animationDelay: '2s' }}></div>
        
        <div className="w-full max-w-md relative z-10">
          <div className="bg-slate-800/40 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-10">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 shadow-lg mb-6">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">RideWise</h1>
              <p className="text-sm text-slate-400 mt-2 font-medium tracking-wide uppercase">AI Support Portal</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Select Role</label>
                <div className="flex bg-slate-900/50 p-1 rounded-xl border border-white/5">
                  <button
                    type="button"
                    onClick={() => setRole('Customer')}
                    className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all ${role === 'Customer' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
                  >
                    Customer
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setRole('Support Agent');
                      setIsLoggedIn(true);
                      setSessionId(crypto.randomUUID());
                      setMessages([]);
                    }}
                    className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all ${role === 'Support Agent' ? 'bg-emerald-500 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
                  >
                    Support Agent
                  </button>
                </div>
              </div>

              {role === 'Customer' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Customer ID</label>
                    <input
                      type="text"
                      placeholder="e.g. CUST0001"
                      value={customerId}
                      onChange={(e) => setCustomerId(e.target.value)}
                      className="w-full bg-slate-900/50 border border-slate-700/50 focus:border-emerald-500 text-slate-100 rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600 focus:ring-2 focus:ring-emerald-500/20"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Mobile Number</label>
                    <input
                      type="text"
                      placeholder="10-digit number"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      className="w-full bg-slate-900/50 border border-slate-700/50 focus:border-emerald-500 text-slate-100 rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600 focus:ring-2 focus:ring-emerald-500/20"
                    />
                  </div>
                </div>
              )}

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-white font-bold py-3.5 px-4 rounded-xl transition-all shadow-lg hover:shadow-emerald-500/25 active:scale-[0.98] mt-4"
              >
                Enter Workspace
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B1120] flex items-center justify-center p-4 font-sans text-slate-100">
      <div className="w-full max-w-6xl h-[90vh] flex bg-slate-800/30 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden">
        
        {/* Sidebar */}
        <div className="w-72 bg-black/40 border-r border-white/10 flex flex-col z-20">
          <div className="p-5 font-bold text-white border-b border-white/10 bg-black/20 flex items-center gap-3">
            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Chat History
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2 scroll-smooth">
             {sessions.length === 0 && <div className="text-slate-500 text-sm p-4 text-center">No past sessions</div>}
             {sessions.map(s => (
               <button 
                  key={s.session_id} 
                  onClick={() => loadSession(s.session_id)} 
                  className={`w-full text-left p-3 rounded-xl transition-all text-sm truncate border ${s.session_id === sessionId ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-100' : 'bg-transparent border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
                >
                 {s.preview}
               </button>
             ))}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col relative overflow-hidden">
          {/* Chat Header */}
        <header className="px-8 py-5 border-b border-white/10 bg-black/20 flex items-center justify-between z-10 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">RideWise Assist</h1>
              <p className="text-xs text-emerald-400 font-medium">
                {role} Mode {role === 'Customer' && `• ${customerId}`}
              </p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button 
              onClick={handleNewChat} 
              className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 text-slate-200 text-sm font-medium rounded-xl transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
              New Chat
            </button>
            <button 
              onClick={handleLogout} 
              className="px-4 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 text-sm font-medium rounded-xl transition-all"
            >
              Switch Role / Login
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto p-8 space-y-6 scroll-smooth bg-gradient-to-b from-transparent to-black/10">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-80">
              <div className="w-20 h-20 bg-slate-800/50 rounded-2xl flex items-center justify-center mb-6 shadow-inner border border-white/5">
                <svg className="w-10 h-10 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-300 mb-2">How can I help you?</h2>
              <p className="text-slate-500 text-center max-w-sm">I have secure access to operational databases and knowledge bases.</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
              <div className={`max-w-[85%] rounded-3xl px-6 py-4 leading-relaxed shadow-lg overflow-x-auto ${
                msg.sender === 'user' 
                  ? 'bg-gradient-to-br from-emerald-500 to-cyan-600 text-white rounded-br-sm' 
                  : msg.sender === 'error'
                    ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30 rounded-bl-sm'
                    : 'bg-slate-800 border border-slate-700/50 text-slate-200 rounded-bl-sm shadow-xl'
              }`}>
                <div 
                  className="prose prose-invert prose-emerald max-w-none text-slate-200 prose-p:leading-relaxed prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-slate-700/50 prose-th:bg-slate-700/30 prose-td:border-slate-700/50"
                  dangerouslySetInnerHTML={{ __html: marked.parse(String(msg.text || "")) }}
                />
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-in fade-in duration-300">
              <div className="bg-slate-800 border border-slate-700/50 rounded-3xl rounded-bl-sm px-6 py-5 flex gap-2 items-center shadow-xl">
                <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <footer className="p-6 bg-slate-900/40 border-t border-white/5 backdrop-blur-md">
          <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-slate-900 border border-slate-700/50 text-slate-200 rounded-2xl focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 block w-full px-6 py-4 outline-none transition-all shadow-inner placeholder:text-slate-500 text-lg"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold py-4 px-8 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-emerald-500/25 active:scale-[0.98] flex items-center justify-center gap-2"
            >
              <span>Send</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </button>
          </form>
        </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
