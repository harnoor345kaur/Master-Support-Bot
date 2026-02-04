"use client";

import { useEffect, useRef, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi 👋 I’m your Support Assistant. Ask me anything about this product and I’ll help you instantly 💛",
      confidence: null,
      sources: [],
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", text: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userMessage.text }),
      });

      const data = await res.json();

      const botMessage = {
        role: "bot",
        text: data.answer || "Sorry, I couldn't generate an answer right now.",
        confidence: data.confidence ?? null,
        sources: data.sources ?? [],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "⚠️ I couldn’t connect to the server. Please check if backend is running.",
          confidence: null,
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onEnterPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-200 bg-white">
          <h1 className="text-xl font-semibold text-slate-900">
            Support Assistant 💬
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Ask me anything about the product & I’ll answer using the documentation.
          </p>
        </div>

        {/* Chat Body */}
        <div className="h-[550px] overflow-y-auto px-6 py-6 space-y-4 bg-slate-50">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.role === "user"
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-800 border border-slate-200"
                }`}
              >
                <div className="whitespace-pre-line">{msg.text}</div>

                {/* Bot Extras */}
                {msg.role === "bot" && msg.confidence !== null && (
                  <div className="mt-3 text-xs text-slate-500">
                    Confidence:{" "}
                    <span className="font-medium text-slate-700">
                      {Math.round(msg.confidence * 100)}%
                    </span>
                  </div>
                )}

                {msg.role === "bot" && msg.sources?.length > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-xs text-slate-600">
                      View sources
                    </summary>
                    <div className="mt-2 space-y-2">
                      {msg.sources.map((src, i) => (
                        <div
                          key={i}
                          className="text-xs bg-slate-100 border border-slate-200 rounded-xl p-2 text-slate-700"
                        >
                          {src}
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-600 shadow-sm">
                Typing<span className="animate-pulse">...</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Box */}
        <div className="px-6 py-4 border-t border-slate-200 bg-white text-slate-600">
          <div className="flex items-center gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onEnterPress}
              placeholder="Type your question here..."
              className="w-full resize-none rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 placeholder:text-slate-300"
              rows={1}
            />
            <button
              onClick={sendMessage}
              className="rounded-2xl bg-slate-900 text-white px-5 py-3 text-sm font-medium hover:bg-slate-800 transition"
            >
              Send
            </button>
          </div>

          <p className="text-xs text-slate-500 mt-2">
            Press <b>Enter</b> to send • <b>Shift + Enter</b> for new line
          </p>
        </div>
      </div>
    </div>
  );
}
