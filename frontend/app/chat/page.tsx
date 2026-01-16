'use client';

import { useState } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  answer: string;
  sources: { type: string; id: string; label: string }[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sources, setSources] = useState<ChatResponse['sources']>([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user' as const, content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    const res = await fetch('/api/backend/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userMessage.content }),
    });
    const data: ChatResponse = await res.json();
    setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }]);
    setSources(data.sources || []);
  };

  return (
    <div className="grid">
      <h1>AdRadar Chat</h1>
      <div className="card" style={{ minHeight: 240 }}>
        {messages.length === 0 && <p>Stelle Fragen zu Ads, Blueprints oder Pages.</p>}
        {messages.map((msg, idx) => (
          <div key={`${msg.role}-${idx}`} style={{ marginBottom: 12 }}>
            <strong>{msg.role === 'user' ? 'Du' : 'Assistant'}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <div className="card">
        <input
          className="input"
          placeholder="Frage eingeben..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="button" style={{ marginTop: 12 }} onClick={sendMessage}>Senden</button>
      </div>
      {sources.length > 0 && (
        <div className="card">
          <h2>Quellen</h2>
          <ul>
            {sources.map((source) => (
              <li key={`${source.type}-${source.id}`}>{source.type}: {source.label}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
