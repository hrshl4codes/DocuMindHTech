import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './QueryView.css';

export default function QueryView({
  documentName,
  conversation,
  citations = [],
  onQuery,
  onReset,
  loading,
  error,
}) {
  const [question, setQuestion] = useState('');
  const conversationEndRef = useRef(null);
  const hasCitations = citations && citations.length > 0;

  useEffect(() => {
    if (conversationEndRef.current && conversationEndRef.current.scrollIntoView) {
      conversationEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  const handleSubmit = () => {
    if (!question.trim() || loading) return;
    onQuery(question.trim());
    setQuestion('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const displayName = documentName
    ? documentName.length > 20
      ? documentName.slice(0, 20) + '…'
      : documentName
    : 'document';

  return (
    <div className="query-view">
      <div className="query-view__topbar">
        <button className="query-view__back" onClick={onReset}>
          ← New document
        </button>
        <span className="query-view__wordmark">DocuMind</span>
        <span className="query-view__file-badge">{displayName}</span>
      </div>

      <div className="query-view__main">
        <div className="query-view__conversation">
          <div className="query-view__messages">
            {conversation.length === 0 && (
              <p className="query-view__empty">Ask a question about your document.</p>
            )}
            {conversation.map((entry, i) => (
              <div key={i} className="query-view__entry">
                <p className="query-view__question">{entry.question}</p>
                <div className="query-view__answer">
                  <div className="query-view__answer-text">
                    <ReactMarkdown>{entry.answer}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="query-view__answer shimmer">
                <div className="query-view__shimmer-line" />
                <div className="query-view__shimmer-line query-view__shimmer-line--short" />
              </div>
            )}
            {error && <p className="query-view__error">{error}</p>}
            <div ref={conversationEndRef} />
          </div>

          <div className="query-view__input-bar">
            <input
              className="query-view__input"
              placeholder="Ask a question about your document..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="query-view__ask-btn"
              onClick={handleSubmit}
              disabled={!question.trim() || loading}
            >
              Ask →
            </button>
          </div>
        </div>

        <div className={`query-view__citations ${hasCitations ? 'query-view__citations--visible' : ''}`}>
          <p className="query-view__citations-label">Sources</p>
          {citations.map((c, i) => (
            <div key={i} className="query-view__citation">
              <span className="query-view__citation-num">[{i + 1}]</span>
              <p className="query-view__citation-excerpt">
                {c.text
                  ? c.text.slice(0, 120) + (c.text.length > 120 ? '…' : '')
                  : ''}
              </p>
              <p className="query-view__citation-meta">
                {[c.source, c.section, c.position].filter(Boolean).join(' · ')}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
