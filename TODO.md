# TODO

## Development Direction

- Target architecture: the daemon should become a runtime management and execution-control system, not the place where business logic lives.
- Current `modules.com/*` and `modules.run/*` are now treated as example legacy implementations of business functionality.
- The target state is a plugin-based model where communication plugins and worker plugins are developed independently from the daemon core.
- Plugins should expose a shared registration and execution API so the daemon can load, supervise, and coordinate them.
- Bidirectional communication should be handled through the daemon dispatcher as a controlled exchange layer between worker plugins and communication plugins.
- Plugins should keep their own libraries, tools, and runtime dependencies, including their own `requirements.txt`.
- Plugins are expected to become independently developed components, most likely in separate repositories.
- Shared libraries tightly coupled to the current implementation, especially `libs.db_models/*`, are not part of the target architecture.
- The current `TODO.md` should be treated as a temporary working plan for analysis on the existing model and can be reordered or rewritten after each architectural decision.

## Status

## Completed Milestones

## P1 - Immediate Work

### Runtime Contracts

### Business Refactoring Preparation

### Functional Risks

## P2 - Next Refactoring Stage

### Service Layer Extraction

### Data Access

### Tests

## P3 - Structural Cleanup

### Naming And Internal API Cleanup

### Documentation Follow-Up

## Backlog
