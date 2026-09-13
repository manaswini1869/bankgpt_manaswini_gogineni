# Architecture

Using Python + FastAPI + Playwright + Pydantic + SQLite/JOSN Artifacts

1. Implemented Architecture 

```

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
    │ Agent Capability API│
    │                     │
    │ list_capabilities() │
    │ invoke_capability() │
    └──────────┬──────────┘
               │
               ▼
          AI Agent

```
Dependency Direction

```
Agent ────────────────┐
                      │
Generator ────────────┼──> Artifact
                      │
Capability API ───────┤
                      │
Replay Engine ────────┘
```

The Artifact is the stable contract as every component has a exactly one dependency.

2. 

| Approach   | Pros                                                                                                                                                                                                 | Cons                                                                                                                                                                       |
| :--------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Screenshot | - Closest to true computer use<br>- Works when DOM is terrible<br>- Naturally extends toward desktop applications                                                                                | - Much harder to make deterministic<br>- Coordinate replay is fragile<br>- Harder to extract structured data<br>- Harder to demonstrate reliable locator strategy<br>- More difficult to test |
| Playwright | - Excellent deterministic replay<br>- Easy screenshots/traces<br>- Easy extraction<br>- Easy testing<br>- Strong waiting primitives<br>- Can use accessibility-oriented locators<br>- Fast to implement | - Doesn't demonstrate the hardest possible legacy surface<br>- DOM assumptions can become brittle<br>- Doesn't directly solve native desktop automation                    |


3. I have decided to make sure that the artifact describes intent and execution, but does not contain an LLM transcript. Which aligns with the requirement for a structured reusable artifact decoupled from the model transcript. I am keeping the generated code out of the artifact this could lead to having two representation that can diverge. I am making this decision to make sure that the artifact remains the single sources of truth.

4. Process


| Option         | Benefit                 | Cost                                           |
| -------------- | ----------------------- | ---------------------------------------------- |
| Single process | Simple, fast, easy demo | Less operational isolation                     |
| Microservices  | Scalable independently  | Huge complexity                                |
| Queue-based    | Async/scalable          | Adds infrastructure without evaluation benefit |


I have used one process where internally each implementation is in a separate modules. 


```
                 DISCOVERY
                    │
              LLM can reason
                    │
                    ▼
             Surface Adapter
                    │
                    ▼
             Artifact Builder
                    │
                    ▼
             ┌──────────────┐
             │   ARTIFACT   │
             └──────┬───────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      Replay      Generate    Capability
       Engine       Code        API
        │           │           │
        └───────────┼───────────┘
                    ▼
             deterministic
                execution
```

- LLM is only in the discovery path.
- The capability API must never call the LLM to figure out what button to press.


# Artifact Schema

# Determinism & Error handling

# Heterogenity & multi-tenant

# Safety

# Cuts