# CLAUDE.md — DocuMind

## 1. Project Overview

DocuMind is a production-oriented Retrieval-Augmented Generation (RAG) system.

Core capabilities:
- Document ingestion (PDF/images)
- Text extraction + chunking
- Embedding generation
- Vector search retrieval
- LLM-based answering with citations

This is NOT a demo project. Treat it as a deployable system.

---

## 2. Primary Objective

Upgrade this system into a **production-grade, portfolio-quality project**.

Focus areas:
- Containerization (Docker, docker-compose)
- CI/CD (GitHub Actions)
- Observability (basic logging, health checks)
- Clean architecture + maintainability
- Clear documentation

DO NOT:
- Rewrite working features
- Add unnecessary AI abstractions (LangChain, agents, etc.)
- Over-engineer (no Kubernetes, no Terraform)

---

## 3. System Architecture

High-level flow:

User → Upload Document  
→ Text Extraction  
→ Chunking  
→ Embeddings  
→ Vector Database  

Query flow:
User Query  
→ Embedding  
→ Vector Search  
→ Reranking  
→ LLM Response  
→ Citation Mapping  

Important:
- Retrieval quality > model choice
- System is pipeline-based, not monolithic

---

## 4. Engineering Principles

Follow strictly:

### Minimalism
- Prefer simple solutions over complex abstractions
- Avoid introducing new frameworks unless necessary

### Stability
- Do not break working functionality
- Make incremental changes only

### Production Thinking
- Every change should move toward:
  - reproducibility
  - deployability
  - reliability

---

## 5. Code Modification Rules

When editing code:

- Do NOT rewrite entire files unless required
- Preserve existing logic unless clearly broken
- Keep functions small and readable
- Avoid deep nesting and over-abstraction

---

## 6. Infrastructure Rules

When adding infrastructure:

### Docker
- Use slim base images
- Use multi-stage builds when applicable
- Run as non-root user

### docker-compose
- Must allow full system to run via:
  docker-compose up

### CI/CD
- Keep pipelines minimal and reliable
- Avoid over-engineered workflows

---

## 7. Documentation Rules

README must be:

- Clear, not verbose
- Technical, not promotional
- Structured:
  - What it does
  - Architecture
  - How to run
  - Tech stack

Avoid:
- AI-style explanations
- Generic filler content

---

## 8. Observability (When Implemented)

If adding observability:

- Start simple:
  - /health endpoint
  - basic logging

Do NOT:
- Add heavy monitoring stacks unless explicitly asked

---

## 9. Git & Commit Rules

All commits must:

- Be small and focused
- Use human-like messages:
  - "add dockerfile for backend"
  - "setup docker-compose"

Never:
- Mention AI, Claude, or automation

---

## 10. Execution Style

When given a task:

1. Plan changes first
2. Modify only necessary files
3. Validate system still works
4. Keep output minimal and precise

---

## 11. Learning Mode (CRITICAL)

For every completed implementation, you MUST generate a report.

This report is REQUIRED.

### Report Requirements

Explain like the reader is a beginner.

Include:

1. What was implemented  
2. Why it was needed  
3. How it fits into the system  
4. How components interact (step-by-step flow)  
5. What alternatives existed and why this was chosen  

### Visuals (REQUIRED where applicable)

Use:
- ASCII diagrams
- Flow diagrams
- Component interaction diagrams

Example:

Frontend → API → Service → DB

### Depth Requirement

The explanation should:
- Build intuition
- Not assume prior knowledge
- Avoid jargon where possible
- Define technical terms when used

---

## 12. Strict Priority Order

Always prioritize in this order:

1. Docker + docker-compose
2. README clarity
3. CI/CD
4. Observability (optional)

Do NOT skip levels.

---

## 13. Failure Conditions

You are doing it wrong if:

- You rewrite large parts of the codebase
- You introduce unnecessary libraries
- The system stops working locally
- The README becomes verbose or generic
- Changes do not improve deployability

---

## 14. Final Goal

Transform DocuMind from:

"student AI project"

into:

"production-ready RAG system with proper engineering practices"

This is a portfolio project, not an experiment.
