# Architecture

The system is a modular monolith with four primary paths: LLM discovery, deterministic replay, an agent-facing capability catalog, and artifact-driven code generation. The key boundary is the capability artifact. The discovery agent is probabilistic; replay is deterministic and never calls the LLM for decisions. FastAPI exposes saved artifacts as typed capabilities, while the code generator compiles the same artifact into a runnable Playwright test.

Python was chosen for its LLM, Pydantic, and browser-automation ecosystem. Playwright was chosen over coordinate-based computer use for the implemented surface because it provides semantic locators, explicit waits, extraction, screenshots, and deterministic replay. The surface is abstracted so a legacy-web or desktop adapter can be added later.

# Artifact schema

Artifacts are versioned Pydantic models serialized to JSON. They contain capability identity/version, the target application, typed inputs/outputs, ordered actions, locator strategy plus rationale, a checkpoint, and safety policy. Raw LLM transcripts are kept as evidence instead of being used as the production automation contract.

The artifact is intentionally richer than a selector list. It gives both a calling agent and a human reviewer enough information to understand what the capability requires, what it returns, and how each target was selected.

# Determinism & error handling

Replay executes the stored step sequence without model decisions. Targeting prefers semantic strategies (test id, role/name, label, text, then CSS). Steps have bounded retries and timeouts, and the final checkpoint is explicitly verified. The result contract distinguishes success, expected business outcomes, recoverable conditions, and hard failures.

The demo treats `MEMBER_NOT_FOUND` as a business outcome. Evidence includes JSONL events plus a failure screenshot. A transient-error simulation is provided for manual testing.

# Heterogeneity & multi-tenant

The artifact depends on an abstract surface contract rather than browser-specific operations. Playwright is the concrete implementation here. A legacy web or desktop implementation can translate the same semantic Target/Action model into the appropriate automation primitives.

For many institutions running the same vendor application, the artifact identity/version can be shared at a base application level, with tenant/version-specific overrides applied to target definitions or entrypoints. Replay should record application version and failure telemetry so drift can be detected without silently changing the artifact.

# Escalation & handoff

The handoff model represents automation ownership explicitly: automating, human control, resume requested, and back to automation. The demo API exposes escalation and resume endpoints and keeps run state in memory. The intended seam is a persistent session manager holding the same browser context while automation pauses, a human operates the visible session, and automation resumes.

# Safety

A policy engine validates the artifact before replay and checks every action at execution time. Domains and action types are allowlisted. Risky capabilities are rejected in this demo rather than silently executed. Logging passes structured data through a redaction layer that removes secret/token/password-like fields. The local demo contains synthetic member data only.

# Cuts

I deliberately left out Kubernetes, distributed queues/workers, production authentication, a persistent artifact database, desktop automation, advanced visual computer use, and an elaborate operator UI. These would add infrastructure breadth without strengthening the core vertical slice. A production implementation would add persistent artifact/session storage, tenant/version resolution, richer operator tooling, stronger approval workflows, and additional surface adapters.
