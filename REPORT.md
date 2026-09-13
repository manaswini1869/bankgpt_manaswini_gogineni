# Architecture

Using Python + FastAPI + Playwright + Pydantic + SQLite/JOSN Artifacts

Implemented Architecture 

                         ┌─────────────────────┐
                         │   Natural language  │
                         │       Goal          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Discovery Agent   │
                         │                     │
                         │  Observe → Decide   │
                         │       → Act         │
                         └──────────┬──────────┘
                                    │
                             successful run
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │      Capability Artifact     │
                    │                              │
                    │ inputs / outputs / steps     │
                    │ locators / checkpoints       │
                    │ errors / safety / version    │
                    └───────┬──────────────┬───────┘
                            │              │
               ┌────────────┘              └─────────────┐
               ▼                                         ▼
    ┌─────────────────────┐                   ┌─────────────────────┐
    │ Deterministic       │                   │ Code Generator      │
    │ Replay Engine       │                   │                     │
    │                     │                   │ Playwright test /   │
    │ NO LLM decisions    │                   │ page object         │
    └──────────┬──────────┘                   └─────────────────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Agent Capability API │
    │                     │
    │ list_capabilities() │
    │ invoke_capability() │
    └──────────┬──────────┘
               │
               ▼
          AI Agent

# Artifact Schema

# Determinism & Error handling

# Heterogenity & multi-tenant

# Safety

# Cuts