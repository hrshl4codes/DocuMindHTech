# Frontend revamp — design spec
**Date:** 2026-05-11  
**Project:** DocuMindHTech-main  
**Status:** Approved

---

## Overview

Replace the existing two-panel vanilla HTML UI with a React SPA that has two full-screen views: an upload view and a query view. The aesthetic is dark ambient — near-black background, glassmorphism cards, sage-green glow blobs, large display typography, pill buttons.

The existing CRA setup (`frontend/src/`) is kept. No new dependencies beyond what is already installed.

---

## Visual design system

### Color tokens (CSS custom properties in `App.css`)

| Token | Value |
|-------|-------|
| `--bg` | `#080808` |
| `--glow-color` | `rgba(100, 140, 100, 0.12)` |
| `--card-bg` | `rgba(255, 255, 255, 0.04)` |
| `--card-border` | `rgba(255, 255, 255, 0.07)` |
| `--input-bg` | `rgba(255, 255, 255, 0.05)` |
| `--input-border` | `rgba(255, 255, 255, 0.10)` |
| `--input-border-focus` | `rgba(255, 255, 255, 0.30)` |
| `--text-primary` | `#ffffff` |
| `--text-secondary` | `rgba(255, 255, 255, 0.50)` |
| `--text-muted` | `rgba(255, 255, 255, 0.25)` |
| `--radius-card` | `16px` |
| `--radius-pill` | `999px` |

### Typography

| Role | Size | Weight | Tracking |
|------|------|--------|----------|
| Display | `clamp(3rem, 6vw, 5rem)` | 700 | `-0.03em` |
| Heading | `1.25rem` | 600 | normal |
| Body | `0.9rem` | 400 | normal |
| Muted label | `0.8rem` | 400 | `0.05em` |

### Buttons

- **Primary:** pill shape, `background: #fff`, `color: #080808`, padding `0.6rem 1.5rem`
- **Ghost:** pill shape, `border: 1px solid rgba(255,255,255,0.2)`, `color: #fff`, same padding

### Cards

```css
background: var(--card-bg);
border: 1px solid var(--card-border);
border-radius: var(--radius-card);
backdrop-filter: blur(12px);
```

### Glow blob

Absolutely positioned, `pointer-events: none`, `z-index: 0`. A radial gradient circle (~600px diameter).  
- Upload view: bottom-left  
- Query view: top-right  

Two versions of the blob exist as separate elements. The upload-view blob and query-view blob each have `transition: opacity 400ms ease`. When the view changes, the active blob fades in and the inactive one fades out.

---

## State machine

`App.js` holds a single `view` state: `'upload' | 'query'`.

```
upload view
  → user selects file/text and clicks Upload
  → handleUpload() POSTs to /api/upload
  → on success: set documentId, transition view to 'query'

query view
  → user types question and clicks Ask
  → handleQuery() POSTs to /api/query
  → on success: append to conversation list, show citations panel
  → "← New document" resets state to 'upload'
```

API calls (`handleUpload`, `handleQuery`) live in `App.js` and are passed as props to child components.

---

## View 1: Upload (`UploadView.jsx`)

**Layout:** centered vertically and horizontally, full viewport height.

**Elements (top to bottom):**
1. `DocuMind` wordmark — top-left, small, `var(--text-secondary)`
2. Display heading: `Drop a document.` / `Ask anything.` — centered, two lines
3. Drop zone card — glass card, dashed border `rgba(255,255,255,0.15)`, min-height 180px
   - Default state: upload icon + "drag & drop or click to upload" + accepted types label
   - Dragover state: border color `#fff`, background `rgba(255,255,255,0.07)`
   - File selected state: filename + file size replace the icon/text
4. Divider: `── or paste text below ──` in muted text
5. Textarea — uses card styling (same `background`, `border`, `border-radius` as glass cards); renders at 1 row height until clicked/focused, then expands to 3 rows via CSS `rows` attribute + `resize: none`
6. Upload button — primary pill, disabled until file or text present, shows "Uploading…" during POST
7. Error message — appears below button if upload fails, muted red text, no loud alert

**Props received from `App.js`:** `onUpload(file, text)`, `loading`, `error`

---

## View 2: Query (`QueryView.jsx`)

**Layout:** full viewport height, three zones:

```
┌──────────────────────────────────────────────────────┐
│  top bar: ← New document   DocuMind   [file badge]   │
├──────────────────────────────┬───────────────────────┤
│  conversation panel (60%)    │  citations panel (40%) │
│  scrollable                  │  slides in on first    │
│                              │  answer                │
├──────────────────────────────┴───────────────────────┤
│  question input (full width) + Ask button            │
└──────────────────────────────────────────────────────┘
```

**Conversation panel:**
- List of `{ question, answer }` pairs, newest at bottom
- Each answer rendered in a glass card
- Inline citation markers `[1]`, `[2]` in answer text
- Loading state: pulsing shimmer card (CSS `@keyframes` on opacity)

**Citations panel:**
- Initially `width: 0; opacity: 0; overflow: hidden`
- On first answer: transitions to `width: 40%; opacity: 1` over 350ms
- Each citation is a glass card: `[n]` number, excerpt (~120 chars), source/page metadata

**Question input bar:**
- Pinned to bottom with `position: sticky; bottom: 0`
- Full-width pill input + "Ask →" ghost button to the right
- Disabled while loading

**Top bar:**
- `← New document` ghost link — calls `onReset()` prop
- `DocuMind` label — centered
- File name badge — right-aligned, muted, truncated to 20 chars

**Props received from `App.js`:** `documentName`, `conversation[]`, `citations[]`, `onQuery(question)`, `onReset()`, `loading`, `error`

---

## Transition (Upload ↔ Query)

No library. Pure CSS class toggle on a wrapper `<div className="view-wrapper">`.

```
.view-wrapper {
  transition: opacity 300ms ease-in, transform 300ms ease-in;
}
.view-wrapper.exiting {
  opacity: 0;
  transform: translateY(-16px);
}
.view-wrapper.entering {
  opacity: 0;
  transform: translateY(16px);
}
.view-wrapper.visible {
  opacity: 1;
  transform: translateY(0);
}
```

Sequence in `App.js`:
1. Set wrapper class to `exiting` (300ms)
2. After 300ms: swap view + set class to `entering`
3. On next frame: set class to `visible` (350ms ease-out)

---

## Component structure

```
frontend/src/
├── App.js                  — view state, API calls, transition timing
├── App.css                 — CSS custom properties, global reset, transition classes
└── components/
    ├── UploadView.jsx
    ├── UploadView.css
    ├── QueryView.jsx
    └── QueryView.css
```

`App.css` defines all tokens. Component CSS files import nothing — they use the tokens via `var(--token-name)`.

---

## What is not changing

- `frontend/index.html` — stays as the fallback (served by `minimal_main.py`)
- `render.yaml` — build command unchanged (`npm install && npm run build`)
- `documind_main.py` / `minimal_main.py` — no backend changes
- `package.json` — no new dependencies added

---

## Out of scope

- Routing (no React Router — two views is not worth a router)
- Dark/light mode toggle
- Mobile-specific layout (responsive adjustments only, not a dedicated mobile design)
- Animation library (Framer Motion, GSAP, etc.)
