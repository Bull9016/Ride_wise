import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';

function App() {
  const [role, setRole] = useState('Customer');
  const [identifier, setIdentifier] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (role === 'Customer' && !identifier.trim()) {
      alert("Please enter your Mobile Number or Customer ID first.");
      return;
    }

    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Map previous messages to OpenAI format for context awareness
      const chatHistory = messages
        .filter(m => m.sender === 'user' || m.sender === 'agent')
        .map(m => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.text }));

      const payload = {
        role: role,
        message: input,
        history: chatHistory,
        mobile_number: identifier.length === 10 && !isNaN(identifier) ? identifier : null,
        customer_id: identifier.startsWith('CUST') ? identifier : null
      };

      const response = await axios.post('http://localhost:8001/api/chat', payload);
      
      setMessages((prev) => [...prev, { text: response.data.answer, sender: 'agent' }]);
    } catch (error) {
      setMessages((prev) => [...prev, { text: "Error: Could not connect to the backend.", sender: 'error' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-indigo-900 flex items-center justify-center p-4 font-sans text-slate-100">
      <div className="w-full max-w-4xl h-[85vh] flex flex-col bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <header className="px-8 py-5 border-b border-white/10 bg-black/20 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">RideWise Assist</h1>
            <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider">AI Support Engine</p>
          </div>
          
          <div className="flex gap-4 items-center">
            <button 
              onClick={() => setMessages([])} 
              className="bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 border border-rose-500/30 text-sm font-medium rounded-lg px-4 py-2 transition-all whitespace-nowrap"
            >
              New Chat
            </button>
            <select 
              value={role} 
              onChange={(e) => setRole(e.target.value)}
              className="bg-slate-900/50 border border-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block w-full p-2.5 outline-none transition-all"
            >
              <option value="Customer">Customer</option>
              <option value="Support Agent">Support Agent</option>
            </select>
            
            {role === 'Customer' && (
              <input
                type="text"
                placeholder="Mobile or CUST0001"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="bg-slate-900/50 border border-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block w-full p-2.5 outline-none transition-all placeholder:text-slate-500"
              />
            )}
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto p-8 space-y-6 scroll-smooth">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-70">
              <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
              <p className="text-lg">How can I help you today?</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-5 py-3.5 leading-relaxed shadow-lg overflow-x-auto ${
                msg.sender === 'user' 
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-br-none' 
                  : msg.sender === 'error'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-slate-700/50 border border-slate-600/50 text-slate-200 rounded-bl-none'
              }`}>
                <div 
                  className="prose prose-invert prose-emerald max-w-none text-slate-200"
                  dangerouslySetInnerHTML={{ __html: marked.parse(String(msg.text || "")) }}
                />
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700/50 border border-slate-600/50 rounded-2xl rounded-bl-none px-5 py-4 flex gap-1.5 items-center shadow-lg">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <footer className="p-6 bg-black/20 border-t border-white/10">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question..."
              className="flex-1 bg-slate-900/50 border border-slate-700 text-slate-200 rounded-xl focus:ring-emerald-500 focus:border-emerald-500 block w-full p-4 outline-none transition-all shadow-inner"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold py-4 px-8 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              Send
            </button>
          </form>
        </footer>
      </div>
    </div>
  );
}

export default App;
