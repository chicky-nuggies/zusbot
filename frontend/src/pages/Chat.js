import React, { useState, useRef, useEffect } from "react";
import { chatAPI } from "../services/api";
import LoadingSpinner from "../components/Common/LoadingSpinner";
import ToolMetadata from "../components/Common/ToolMetadata";
import "./Chat.css";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setError(null);

    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      type: "user",
      content: userMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(userMessage, sessionId);

      // Update session ID if this is the first message
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }

      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: response.response,
        timestamp: new Date(),
        toolCalls: response.tool_calls || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to send message. Please try again."
      );
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  };

  return (
    <div className="chat-page">
      <h1 className="page-title">Chat Assistant</h1>
      <p className="page-subtitle">
        Ask me anything about Zus Coffee - our products, locations, services,
        and more!
      </p>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <p>👋 Welcome! How can I help you today?</p>
              <div className="chat-suggestions">
                <button
                  className="suggestion-btn"
                  onClick={() =>
                    setInputValue("What are your popular coffee drinks?")
                  }
                >
                  What are your popular coffee drinks?
                </button>
                <button
                  className="suggestion-btn"
                  onClick={() => setInputValue("Find outlets near KLCC")}
                >
                  Find outlets near KLCC
                </button>
                <button
                  className="suggestion-btn"
                  onClick={() => setInputValue("What's your opening hours?")}
                >
                  What's your opening hours?
                </button>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
              {message.toolCalls && message.toolCalls.length > 0 && (
                <ToolMetadata toolCalls={message.toolCalls} />
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <LoadingSpinner size="small" text="Thinking..." />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit} className="chat-form">
          <div className="chat-input-container">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message here..."
              className="chat-input"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="chat-send-btn"
              disabled={isLoading || !inputValue.trim()}
            >
              {isLoading ? "⏳" : "📤"}
            </button>
          </div>
          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearChat}
              className="clear-chat-btn"
            >
              🗑️ Clear Chat
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

export default Chat;
