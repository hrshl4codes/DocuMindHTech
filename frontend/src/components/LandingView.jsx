import React from 'react';
import './LandingView.css';

export default function LandingView({ onOpenApp }) {
  return (
    <div className="landing">
      <div className="landing__noise" aria-hidden="true" />
      <div className="landing__glow" aria-hidden="true" />

      {/* ── Nav ───────────────────────────────────────────── */}
      <nav className="landing__nav">
        <div className="landing__logo">
          <span className="landing__logo-mark">◉</span>
          <span className="landing__logo-text">DocuMind</span>
        </div>
        <div className="landing__nav-links">
          <a href="#features">Features</a>
          <a href="#pipeline">Pipeline</a>
          <a href="#stack">Stack</a>
          <a
            href="https://github.com/hrshl4codes/DocuMindHTech"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub ↗
          </a>
        </div>
        <button className="landing__nav-cta" onClick={onOpenApp}>
          Open App →
        </button>
      </nav>

      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="landing__hero">

        {/* Horizontal rail lines (SVG) */}
        <svg
          className="landing__rails-svg"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          {/* Left-top rail */}
          <line x1="2"  y1="33" x2="22" y2="33" stroke="rgba(255,255,255,0.06)" strokeWidth="0.12" />
          {/* Left-bottom rail */}
          <line x1="0"  y1="67" x2="19" y2="67" stroke="rgba(255,255,255,0.06)" strokeWidth="0.12" />
          {/* Right-top rail */}
          <line x1="79" y1="28" x2="98" y2="28" stroke="rgba(255,255,255,0.06)" strokeWidth="0.12" />
          {/* Right-bottom rail */}
          <line x1="81" y1="67" x2="98" y2="67" stroke="rgba(255,255,255,0.06)" strokeWidth="0.12" />
        </svg>

        {/* Left-top station: Parser */}
        <div className="landing__station landing__station--lt">
          <div className="landing__station-circle">▲</div>
          <div className="landing__station-text">
            <span className="landing__station-name">• Parser</span>
            <span className="landing__station-sub">PDF · DOCX · TXT</span>
          </div>
        </div>

        {/* Left-bottom station: Embeddings */}
        <div className="landing__station landing__station--lb">
          <div className="landing__station-circle landing__station-circle--net">⬡</div>
          <div className="landing__station-text">
            <span className="landing__station-name">• Embeddings</span>
            <span className="landing__station-sub">1536-d vectors</span>
          </div>
        </div>

        {/* Right-top station: Retrieval */}
        <div className="landing__station landing__station--rt">
          <div className="landing__station-text landing__station-text--right">
            <span className="landing__station-name">• Retrieval</span>
            <span className="landing__station-sub">Semantic search</span>
          </div>
          <div className="landing__station-circle">✳</div>
        </div>

        {/* Right-bottom station: Citations */}
        <div className="landing__station landing__station--rb">
          <div className="landing__station-text landing__station-text--right">
            <span className="landing__station-name">• Citations</span>
            <span className="landing__station-sub">Source-linked</span>
          </div>
          <div className="landing__station-circle">◈</div>
        </div>

        {/* ── Center content ─────────────────────────────── */}
        <div className="landing__center">
          <div className="landing__play" aria-hidden="true">▶</div>

          <div className="landing__badge">
            <span className="landing__badge-dot">◉</span>
            RAG-powered document intelligence →
          </div>

          <h1 className="landing__heading">DocuMind</h1>

          <p className="landing__slogan">Upload once. Ask anything.</p>

          <p className="landing__sub">
            Drop a PDF, paste text, or upload any document —<br />
            get cited answers in seconds, powered by retrieval-augmented generation.
          </p>

          <div className="landing__ctas">
            <button className="landing__cta-dark" onClick={onOpenApp}>
              Open App ↗
            </button>
            <a
              className="landing__cta-light"
              href="https://github.com/hrshl4codes/DocuMindHTech"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </div>
        </div>

        {/* Bar visualizer */}
        <div className="landing__bars" aria-hidden="true">
          {[
            { h: '55%', d: '0s'    },
            { h: '90%', d: '0.3s'  },
            { h: '100%',d: '0.15s' },
            { h: '70%', d: '0.45s' },
            { h: '40%', d: '0.1s'  },
          ].map((b, i) => (
            <div key={i} className="landing__bar" style={{ '--h': b.h, '--d': b.d }} />
          ))}
        </div>

        {/* Bottom indicators */}
        <div className="landing__scroll">
          <span className="landing__scroll-icon">↓</span>
          <span className="landing__scroll-text">01/02 · Scroll down</span>
        </div>

        <div className="landing__section-label" aria-hidden="true">
          RAG horizons
          <div className="landing__section-line" />
        </div>
      </section>

      {/* ── Tech strip ────────────────────────────────────── */}
      <div className="landing__strip">
        <span className="landing__strip-label">Powered by</span>
        <div className="landing__strip-logos">
          {['OpenAI', 'Cohere', 'Pinecone', 'FastAPI', 'React', 'Render'].map((name) => (
            <span key={name} className="landing__strip-logo">{name}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
