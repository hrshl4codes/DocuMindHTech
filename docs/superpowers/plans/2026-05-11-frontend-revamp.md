# Frontend Revamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing two-panel React UI with a dark ambient two-state SPA (UploadView → QueryView) matching the design spec.

**Architecture:** `App.js` owns view state (`'upload' | 'query'`), all API calls, and the CSS-class-based view transition. `UploadView` and `QueryView` are pure presentational components that receive props. No new dependencies.

**Tech Stack:** React 18, CRA, CSS custom properties, axios (already installed), @testing-library/react (already installed)

---

## File map

| File | Action | Responsibility |
|------|--------|----------------|
| `frontend/src/index.css` | Modify | Remove old purple gradient; keep only bare reset |
| `frontend/src/App.css` | Rewrite | CSS tokens, base classes (`.card`, `.btn-primary`, `.btn-ghost`, `.input-pill`), glow blobs, view transition wrapper, shimmer keyframe |
| `frontend/src/App.js` | Rewrite | view state, transition timing, `handleUpload`, `handleQuery`, `handleReset`, render |
| `frontend/src/components/UploadView.jsx` | Create | Drop zone, textarea, upload button |
| `frontend/src/components/UploadView.css` | Create | UploadView layout + styles |
| `frontend/src/components/QueryView.jsx` | Create | Top bar, conversation list, citations panel, input bar |
| `frontend/src/components/QueryView.css` | Create | QueryView layout + styles |
| `frontend/src/components/UploadView.test.jsx` | Create | Render + interaction tests |
| `frontend/src/components/QueryView.test.jsx` | Create | Render + interaction tests |

---

## Task 1: Update index.css and write App.css design system

**Files:**
- Modify: `frontend/src/index.css`
- Rewrite: `frontend/src/App.css`

- [ ] **Step 1: Replace index.css**

Open `frontend/src/index.css` and replace its entire contents with:

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #root {
  height: 100%;
}
```

- [ ] **Step 2: Write App.css**

Replace `frontend/src/App.css` entirely with:

```css
:root {
  --bg: #080808;
  --glow-color: rgba(100, 140, 100, 0.12);
  --card-bg: rgba(255, 255, 255, 0.04);
  --card-border: rgba(255, 255, 255, 0.07);
  --input-bg: rgba(255, 255, 255, 0.05);
  --input-border: rgba(255, 255, 255, 0.10);
  --input-border-focus: rgba(255, 255, 255, 0.30);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.50);
  --text-muted: rgba(255, 255, 255, 0.25);
  --radius-card: 16px;
  --radius-pill: 999px;
}

html, body, #root {
  background: var(--bg);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.9rem;
  -webkit-font-smoothing: antialiased;
}

/* App shell */
.app {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

/* Glow blobs */
.glow-blob {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--glow-color) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
  transition: opacity 400ms ease;
}

.glow-blob--upload {
  bottom: -100px;
  left: -100px;
  opacity: 1;
}

.glow-blob--query {
  top: -100px;
  right: -100px;
  opacity: 0;
}

.app.view-query .glow-blob--upload { opacity: 0; }
.app.view-query .glow-blob--query  { opacity: 1; }

/* View transition wrapper */
.view-wrapper {
  position: relative;
  z-index: 1;
}

.view-wrapper.exiting {
  transition: opacity 300ms ease-in, transform 300ms ease-in;
  opacity: 0;
  transform: translateY(-16px);
}

.view-wrapper.entering {
  transition: none;
  opacity: 0;
  transform: translateY(16px);
}

.view-wrapper.visible {
  transition: opacity 350ms ease-out, transform 350ms ease-out;
  opacity: 1;
  transform: translateY(0);
}

/* Card base */
.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-card);
  backdrop-filter: blur(12px);
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-pill);
  border: none;
  background: #ffffff;
  color: #080808;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 200ms ease;
}
.btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-primary:not(:disabled):hover { opacity: 0.85; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 200ms ease, background 200ms ease;
}
.btn-ghost:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-ghost:not(:disabled):hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
}

/* Pill input base */
.input-pill {
  width: 100%;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-pill);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 200ms ease;
}
.input-pill::placeholder { color: var(--text-muted); }
.input-pill:focus { border-color: var(--input-border-focus); }

/* Shimmer keyframe */
@keyframes shimmer {
  0%, 100% { opacity: 0.3; }
  50%       { opacity: 0.7; }
}
.shimmer { animation: shimmer 1.5s ease-in-out infinite; }
```

- [ ] **Step 3: Start the dev server and verify the page is black with no errors**

```bash
cd frontend && npm start
```

Expected: browser opens, page is near-black `#080808`, no console errors, `#root` fills full height.

- [ ] **Step 4: Commit**

```bash
cd frontend && git add src/index.css src/App.css && git commit -m "add design system tokens and base classes"
```

---

## Task 2: UploadView component

**Files:**
- Create: `frontend/src/components/UploadView.jsx`
- Create: `frontend/src/components/UploadView.css`
- Create: `frontend/src/components/UploadView.test.jsx`

- [ ] **Step 1: Create the components directory**

```bash
mkdir -p frontend/src/components
```

- [ ] **Step 2: Write the failing tests**

Create `frontend/src/components/UploadView.test.jsx`:

```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UploadView from './UploadView';

const noop = () => {};

test('renders wordmark', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByText('DocuMind')).toBeInTheDocument();
});

test('renders heading', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByText(/Drop a document/i)).toBeInTheDocument();
  expect(screen.getByText(/Ask anything/i)).toBeInTheDocument();
});

test('upload button is disabled with no input', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByRole('button', { name: /upload/i })).toBeDisabled();
});

test('upload button calls onUpload when text is provided', () => {
  const onUpload = jest.fn();
  render(<UploadView onUpload={onUpload} loading={false} error="" />);
  fireEvent.change(screen.getByPlaceholderText(/Paste your document/i), {
    target: { value: 'some document text' }
  });
  fireEvent.click(screen.getByRole('button', { name: /upload/i }));
  expect(onUpload).toHaveBeenCalledWith(null, 'some document text');
});

test('shows error message when error prop is set', () => {
  render(<UploadView onUpload={noop} loading={false} error="Upload failed" />);
  expect(screen.getByText('Upload failed')).toBeInTheDocument();
});

test('shows Uploading… text when loading', () => {
  render(<UploadView onUpload={noop} loading={true} error="" />);
  expect(screen.getByRole('button', { name: /uploading/i })).toBeInTheDocument();
});
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
cd frontend && npm test -- --watchAll=false --testPathPattern="UploadView.test"
```

Expected: 6 tests fail with "Cannot find module './UploadView'"

- [ ] **Step 4: Create UploadView.css**

Create `frontend/src/components/UploadView.css`:

```css
.upload-view {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.upload-view__wordmark {
  position: absolute;
  top: 2rem;
  left: 2rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.upload-view__content {
  width: 100%;
  max-width: 560px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.upload-view__heading {
  font-size: clamp(3rem, 6vw, 5rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
  text-align: center;
  margin-bottom: 0.5rem;
}

.upload-view__heading--dim {
  color: var(--text-secondary);
}

.upload-view__dropzone {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: 1.5px dashed rgba(255, 255, 255, 0.15);
  cursor: pointer;
  padding: 2rem;
  transition: border-color 200ms ease, background 200ms ease;
}

.upload-view__dropzone--dragover {
  border-color: #ffffff;
  background: rgba(255, 255, 255, 0.07);
}

.upload-view__dropzone--filled {
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.2);
}

.upload-view__dropzone-icon {
  font-size: 1.75rem;
  color: var(--text-secondary);
}

.upload-view__dropzone-text {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.upload-view__dropzone-types {
  color: var(--text-muted);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

.upload-view__file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.upload-view__file-name {
  font-size: 0.95rem;
  color: var(--text-primary);
}

.upload-view__file-size {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.upload-view__divider {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

.upload-view__textarea {
  width: 100%;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-card);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  resize: none;
  transition: border-color 200ms ease;
}

.upload-view__textarea::placeholder { color: var(--text-muted); }
.upload-view__textarea:focus { border-color: var(--input-border-focus); }

.upload-view__submit {
  align-self: center;
  min-width: 140px;
  justify-content: center;
}

.upload-view__error {
  text-align: center;
  color: rgba(255, 100, 100, 0.8);
  font-size: 0.85rem;
}
```

- [ ] **Step 5: Create UploadView.jsx**

Create `frontend/src/components/UploadView.jsx`:

```jsx
import React, { useState, useRef } from 'react';
import './UploadView.css';

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function UploadView({ onUpload, loading, error }) {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [dragover, setDragover] = useState(false);
  const [textFocused, setTextFocused] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => { e.preventDefault(); setDragover(true); };
  const handleDragLeave = () => setDragover(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) setFile(selected);
  };

  const canUpload = (file || text.trim()) && !loading;

  return (
    <div className="upload-view">
      <span className="upload-view__wordmark">DocuMind</span>

      <div className="upload-view__content">
        <h1 className="upload-view__heading">
          Drop a document.<br />
          <span className="upload-view__heading--dim">Ask anything.</span>
        </h1>

        <div
          className={[
            'upload-view__dropzone',
            'card',
            dragover ? 'upload-view__dropzone--dragover' : '',
            file ? 'upload-view__dropzone--filled' : '',
          ].join(' ')}
          onClick={() => fileInputRef.current.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="upload-view__file-info">
              <span className="upload-view__file-name">{file.name}</span>
              <span className="upload-view__file-size">{formatFileSize(file.size)}</span>
            </div>
          ) : (
            <>
              <div className="upload-view__dropzone-icon">↑</div>
              <p className="upload-view__dropzone-text">drag & drop or click to upload</p>
              <p className="upload-view__dropzone-types">PDF · DOCX · TXT · MD</p>
            </>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <p className="upload-view__divider">── or paste text below ──</p>

        <textarea
          className="upload-view__textarea card"
          placeholder="Paste your document text here..."
          value={text}
          rows={textFocused || text ? 3 : 1}
          onFocus={() => setTextFocused(true)}
          onBlur={() => setTextFocused(!!text)}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          className="btn-primary upload-view__submit"
          onClick={() => onUpload(file, text)}
          disabled={!canUpload}
        >
          {loading ? 'Uploading…' : 'Upload'}
        </button>

        {error && <p className="upload-view__error">{error}</p>}
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Run tests to confirm they pass**

```bash
cd frontend && npm test -- --watchAll=false --testPathPattern="UploadView.test"
```

Expected output:
```
PASS src/components/UploadView.test.jsx
  ✓ renders wordmark
  ✓ renders heading
  ✓ upload button is disabled with no input
  ✓ upload button calls onUpload when text is provided
  ✓ shows error message when error prop is set
  ✓ shows Uploading… text when loading

Test Suites: 1 passed, 1 total
Tests:       6 passed, 6 total
```

- [ ] **Step 7: Commit**

```bash
cd frontend && git add src/components/UploadView.jsx src/components/UploadView.css src/components/UploadView.test.jsx && git commit -m "add UploadView component"
```

---

## Task 3: QueryView component

**Files:**
- Create: `frontend/src/components/QueryView.jsx`
- Create: `frontend/src/components/QueryView.css`
- Create: `frontend/src/components/QueryView.test.jsx`

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/components/QueryView.test.jsx`:

```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import QueryView from './QueryView';

const noop = () => {};
const defaultProps = {
  documentName: 'report.pdf',
  conversation: [],
  citations: [],
  onQuery: noop,
  onReset: noop,
  loading: false,
  error: '',
};

test('renders top bar with document name', () => {
  render(<QueryView {...defaultProps} />);
  expect(screen.getByText('report.pdf')).toBeInTheDocument();
  expect(screen.getByText('DocuMind')).toBeInTheDocument();
});

test('renders empty state message', () => {
  render(<QueryView {...defaultProps} />);
  expect(screen.getByText(/Ask a question about your document/i)).toBeInTheDocument();
});

test('renders conversation entries', () => {
  const conversation = [
    { question: 'What is this?', answer: 'It is a test document.' }
  ];
  render(<QueryView {...defaultProps} conversation={conversation} />);
  expect(screen.getByText('What is this?')).toBeInTheDocument();
  expect(screen.getByText('It is a test document.')).toBeInTheDocument();
});

test('citations panel is hidden with no citations', () => {
  const { container } = render(<QueryView {...defaultProps} />);
  const panel = container.querySelector('.query-view__citations');
  expect(panel).not.toHaveClass('query-view__citations--visible');
});

test('citations panel is visible when citations exist', () => {
  const citations = [{ text: 'Some source text here.', source: 'report.pdf', section: 'p1', position: '1' }];
  const { container } = render(<QueryView {...defaultProps} citations={citations} />);
  const panel = container.querySelector('.query-view__citations');
  expect(panel).toHaveClass('query-view__citations--visible');
});

test('calls onQuery when Ask button is clicked with a question', () => {
  const onQuery = jest.fn();
  render(<QueryView {...defaultProps} onQuery={onQuery} />);
  fireEvent.change(screen.getByPlaceholderText(/Ask a question/i), {
    target: { value: 'Who wrote this?' }
  });
  fireEvent.click(screen.getByRole('button', { name: /ask/i }));
  expect(onQuery).toHaveBeenCalledWith('Who wrote this?');
});

test('calls onReset when New document is clicked', () => {
  const onReset = jest.fn();
  render(<QueryView {...defaultProps} onReset={onReset} />);
  fireEvent.click(screen.getByRole('button', { name: /New document/i }));
  expect(onReset).toHaveBeenCalled();
});

test('truncates document name longer than 20 chars', () => {
  render(<QueryView {...defaultProps} documentName="a_very_long_filename_that_exceeds_limit.pdf" />);
  expect(screen.getByText('a_very_long_filename…')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd frontend && npm test -- --watchAll=false --testPathPattern="QueryView.test"
```

Expected: 8 tests fail with "Cannot find module './QueryView'"

- [ ] **Step 3: Create QueryView.css**

Create `frontend/src/components/QueryView.css`:

```css
.query-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Top bar */
.query-view__topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}

.query-view__back {
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
}

.query-view__wordmark {
  font-size: 0.9rem;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.query-view__file-badge {
  font-size: 0.8rem;
  color: var(--text-muted);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Main layout */
.query-view__main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Conversation panel */
.query-view__conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid var(--card-border);
}

.query-view__messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.query-view__messages::-webkit-scrollbar { width: 4px; }
.query-view__messages::-webkit-scrollbar-track { background: transparent; }
.query-view__messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.query-view__empty {
  color: var(--text-muted);
  text-align: center;
  margin-top: 4rem;
}

.query-view__entry {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.query-view__question {
  color: var(--text-secondary);
  font-size: 0.85rem;
  padding-left: 0.75rem;
  border-left: 2px solid rgba(255, 255, 255, 0.1);
}

.query-view__answer {
  padding: 1.25rem 1.5rem;
}

.query-view__answer-text {
  line-height: 1.7;
  color: var(--text-primary);
}

/* Shimmer skeleton */
.query-view__shimmer-line {
  height: 14px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  margin-bottom: 0.75rem;
}

.query-view__shimmer-line--short {
  width: 60%;
  margin-bottom: 0;
}

.query-view__error {
  color: rgba(255, 100, 100, 0.8);
  font-size: 0.85rem;
  text-align: center;
}

/* Input bar */
.query-view__input-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  border-top: 1px solid var(--card-border);
  flex-shrink: 0;
  background: var(--bg);
}

.query-view__input { flex: 1; }

.query-view__ask-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

/* Citations panel */
.query-view__citations {
  width: 0;
  opacity: 0;
  overflow: hidden;
  transition: width 350ms ease, opacity 350ms ease;
  display: flex;
  flex-direction: column;
}

.query-view__citations--visible {
  width: 40%;
  opacity: 1;
  overflow-y: auto;
  padding: 1.5rem;
  gap: 1rem;
}

.query-view__citations--visible::-webkit-scrollbar { width: 4px; }
.query-view__citations--visible::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.query-view__citations-label {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.query-view__citation {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.query-view__citation-num {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.query-view__citation-excerpt {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-secondary);
  font-style: italic;
}

.query-view__citation-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}
```

- [ ] **Step 4: Create QueryView.jsx**

Create `frontend/src/components/QueryView.jsx`:

```jsx
import React, { useState, useRef, useEffect } from 'react';
import './QueryView.css';

export default function QueryView({
  documentName,
  conversation,
  citations,
  onQuery,
  onReset,
  loading,
  error,
}) {
  const [question, setQuestion] = useState('');
  const conversationEndRef = useRef(null);
  const hasCitations = citations && citations.length > 0;

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
        <button className="btn-ghost query-view__back" onClick={onReset}>
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
                <div className="query-view__answer card">
                  <p className="query-view__answer-text">{entry.answer}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="query-view__answer card shimmer">
                <div className="query-view__shimmer-line" />
                <div className="query-view__shimmer-line query-view__shimmer-line--short" />
              </div>
            )}
            {error && <p className="query-view__error">{error}</p>}
            <div ref={conversationEndRef} />
          </div>

          <div className="query-view__input-bar">
            <input
              className="input-pill query-view__input"
              placeholder="Ask a question about your document..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="btn-ghost query-view__ask-btn"
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
            <div key={i} className="query-view__citation card">
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
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
cd frontend && npm test -- --watchAll=false --testPathPattern="QueryView.test"
```

Expected output:
```
PASS src/components/QueryView.test.jsx
  ✓ renders top bar with document name
  ✓ renders empty state message
  ✓ renders conversation entries
  ✓ citations panel is hidden with no citations
  ✓ citations panel is visible when citations exist
  ✓ calls onQuery when Ask button is clicked with a question
  ✓ calls onReset when New document is clicked
  ✓ truncates document name longer than 20 chars

Test Suites: 1 passed, 1 total
Tests:       8 passed, 8 total
```

- [ ] **Step 6: Commit**

```bash
cd frontend && git add src/components/QueryView.jsx src/components/QueryView.css src/components/QueryView.test.jsx && git commit -m "add QueryView component"
```

---

## Task 4: Rewrite App.js and wire everything together

**Files:**
- Rewrite: `frontend/src/App.js`

- [ ] **Step 1: Replace App.js**

Replace the entire contents of `frontend/src/App.js` with:

```jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import UploadView from './components/UploadView';
import QueryView from './components/QueryView';
import './App.css';

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? ''
    : 'https://documindrex.onrender.com');

export default function App() {
  const [view, setView] = useState('upload');
  const [transitionClass, setTransitionClass] = useState('visible');
  const [documentId, setDocumentId] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [conversation, setConversation] = useState([]);
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const transitionTimeout = useRef(null);

  useEffect(() => () => clearTimeout(transitionTimeout.current), []);

  const transitionTo = (nextView) => {
    setTransitionClass('exiting');
    transitionTimeout.current = setTimeout(() => {
      setView(nextView);
      setTransitionClass('entering');
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setTransitionClass('visible'));
      });
    }, 300);
  };

  const handleUpload = async (file, text) => {
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else {
        formData.append('text', text);
      }
      const res = await axios.post(`${API_BASE_URL}/api/upload`, formData);
      if (res.data.success) {
        setDocumentId(res.data.document_id);
        setDocumentName(file ? file.name : 'pasted text');
        setConversation([]);
        setCitations([]);
        transitionTo('query');
      } else {
        setError(res.data.error || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async (question) => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API_BASE_URL}/api/query`, {
        document_id: documentId,
        question,
      });
      if (res.data.success) {
        setConversation((prev) => [...prev, { question, answer: res.data.answer }]);
        if (res.data.citations) setCitations(res.data.citations);
      } else {
        setError(res.data.error || 'Query failed');
      }
    } catch (err) {
      setError('Query failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    transitionTo('upload');
    setDocumentId(null);
    setDocumentName('');
    setConversation([]);
    setCitations([]);
    setError('');
  };

  return (
    <div className={`app ${view === 'query' ? 'view-query' : ''}`}>
      <div className="glow-blob glow-blob--upload" />
      <div className="glow-blob glow-blob--query" />
      <div className={`view-wrapper ${transitionClass}`}>
        {view === 'upload' ? (
          <UploadView onUpload={handleUpload} loading={loading} error={error} />
        ) : (
          <QueryView
            documentName={documentName}
            conversation={conversation}
            citations={citations}
            onQuery={handleQuery}
            onReset={handleReset}
            loading={loading}
            error={error}
          />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Run all tests to confirm nothing broke**

```bash
cd frontend && npm test -- --watchAll=false
```

Expected output:
```
PASS src/components/UploadView.test.jsx
PASS src/components/QueryView.test.jsx

Test Suites: 2 passed, 2 total
Tests:       14 passed, 14 total
```

- [ ] **Step 3: Verify in browser**

```bash
cd frontend && npm start
```

Check all of the following manually:

1. Page loads as dark (#080808), green glow blob visible bottom-left
2. Heading reads "Drop a document. / Ask anything."
3. Drop zone shows upload icon and accepted types
4. Textarea starts at 1 row, expands to 3 on focus
5. Upload button is disabled until text is entered or file selected
6. Enter any text → click Upload → page fades out and fades into query view
7. Query view: top bar shows "← New document", "DocuMind", filename badge
8. Type a question → press Enter or click Ask → shimmer loading card appears
9. Answer appears in a glass card; citations panel slides in from the right if citations are returned
10. Click "← New document" → fades back to upload view, glow blob repositions

- [ ] **Step 4: Final commit**

```bash
cd frontend && git add src/App.js && git commit -m "wire up App.js with view state machine and transitions"
```

---

## Task 5: Production build verification

**Files:** none (verification only)

- [ ] **Step 1: Run the production build**

```bash
cd frontend && npm run build
```

Expected: build completes with no errors. Output in `frontend/build/`.

- [ ] **Step 2: Serve via documind_main.py and verify**

```bash
cd .. && python documind_main.py
```

Open `http://localhost:8000`. Verify the React build is served (not the fallback `index.html`) — you should see the same dark UI as in dev.

- [ ] **Step 3: Final commit**

```bash
git add frontend/build && git commit -m "add production frontend build"
```

> Note: committing the build is optional. If `render.yaml` builds it on deploy, you can add `frontend/build` to `.gitignore` instead.
