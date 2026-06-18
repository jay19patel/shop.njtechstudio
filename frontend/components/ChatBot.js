"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Sheet, SheetContent, SheetTrigger, SheetTitle, SheetDescription } from './ui/sheet';
import { MessageCircle, Send, Sparkles, User, Bot } from 'lucide-react';

export default function ChatBot() {
  const [messages, setMessages] = useState([
    {
      id: 'init',
      sender: 'bot',
      text: 'Hi there! 👋 Welcome to NJShop. How can we help you today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: input.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulated reply delay
    setTimeout(() => {
      setIsTyping(false);
      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: 'Thank you for connecting with NJ Support!',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMessage]);
    }, 1000);
  };

  return (
    <Sheet>
      {/* Floating Chat Button (Bottom-Left) */}
      <SheetTrigger asChild>
        <button
          className="fixed bottom-6 left-6 z-40 p-4 rounded-none bg-slate-900 text-white shadow-xl hover:bg-slate-800 transition-all hover:scale-105 active:scale-95 group focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2"
          aria-label="Open support chat"
        >
          <div className="relative">
            <MessageCircle className="w-6 h-6 transition-transform group-hover:rotate-12" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-none bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-none h-3 w-3 bg-green-500 border border-slate-900"></span>
            </span>
          </div>
        </button>
      </SheetTrigger>

      {/* Chat Side Drawer (Opens from Left) */}
      <SheetContent side="left" className="flex flex-col h-full w-full sm:max-w-md p-0 overflow-hidden rounded-none">
        <span className="sr-only">
          <SheetTitle>NJ Support Chat</SheetTitle>
          <SheetDescription>Customer support chat assistant for NJShop</SheetDescription>
        </span>
        
        {/* Chat Header (Clean & Professional) */}
        <div className="p-4 border-b border-slate-100 bg-slate-900 text-white flex items-center gap-3">
          <div className="w-10 h-10 rounded-none bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center shadow-md shrink-0">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold tracking-wider uppercase text-xs">NJ Support</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-none bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-none h-1.5 w-1.5 bg-green-500"></span>
              </span>
              <span className="text-[9px] text-green-400 font-black uppercase tracking-widest">Online</span>
            </div>
          </div>
        </div>

        {/* Messages List Area */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-slate-50">
          {messages.map((msg) => {
            const isBot = msg.sender === 'bot';
            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${isBot ? 'self-start' : 'self-end flex-row-reverse'}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-none flex items-center justify-center shadow-sm shrink-0 ${
                  isBot ? 'bg-white text-slate-950 border border-slate-100' : 'bg-slate-900 text-white'
                }`}>
                  {isBot ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                </div>

                {/* Bubble content */}
                <div className="flex flex-col gap-1">
                  <div className={`rounded-none px-4 py-2.5 text-xs font-sans shadow-sm leading-relaxed border ${
                    isBot 
                      ? 'bg-white text-slate-950 border-slate-100' 
                      : 'bg-slate-900 text-white border-slate-900'
                  }`}>
                    <p>{msg.text}</p>
                  </div>
                  <span className={`text-[9px] font-black uppercase tracking-wider text-slate-400 ${
                    isBot ? 'text-left ml-1' : 'text-right mr-1'
                  }`}>
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3 max-w-[85%] self-start">
              <div className="w-8 h-8 rounded-none bg-white text-slate-950 border border-slate-100 flex items-center justify-center shadow-sm shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-1 bg-white border border-slate-100 rounded-none px-4 py-3 shadow-sm">
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-none animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-none animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-none animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Footer Area */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-100 bg-white flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-grow bg-slate-50 border border-slate-200 text-slate-900 rounded-none px-4 py-2.5 text-xs font-semibold focus:outline-none focus:border-slate-400 focus:bg-white transition-all placeholder:text-slate-400"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="p-2.5 rounded-none bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all focus:outline-none"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

      </SheetContent>
    </Sheet>
  );
}
