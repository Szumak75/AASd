# TODO

## Status

- Current focus: refactoring preparation after documentation normalization.
- Public API boundary: runtime and module layer.
- Internal integration layer: `libs/db_models/*`.

## Completed Milestones

- Normalize shared core docstrings in `libs/app.py`, `libs/base/classes.py`, `libs/conf.py`, `libs/com/message.py`, and `server/daemon.py`.
- Align module docstrings in `modules/run/` and `modules/com/` with the current project template and section rules.
- Normalize ORM docstrings across `libs/db_models/`.
- Add Sphinx-based API generation and HTML build workflow.
- Add dedicated documentation pages for architecture, API, and API surface policy.
- Review and update installation documentation for the Python 3.11 target environment.
- Decide and document that SQLAlchemy models remain outside the public API reference.

## P1 - Immediate Work

### Runtime Contracts

- [ ] Define the stable lifecycle contract for runtime modules: init, config apply, run, sleep, stop, stopped state.
- [ ] Document queue ownership and message-routing rules between daemon, dispatcher, `modules/run/*`, and `modules/com/*`.
- [ ] Define the supported message payload contract for `libs.com.message.Message`.
- [ ] Review whether `BModule` should remain a mixed-responsibility class or be split into smaller mixins/contracts.

### Business Refactoring Preparation

- [ ] Separate orchestration concerns from business rules in `modules/run/mlmspayment.py`.
- [ ] Separate orchestration concerns from business rules in `modules/run/mlmstariff.py`.
- [ ] Identify extraction points for service objects in `modules/run/micmp.py`.
- [ ] Identify data-fetching, decision, and message-building boundaries in each business module.

### Functional Risks

- [ ] Fix config generation bug: if the configuration file does not exist, running with the `-U` flag duplicates section descriptions.
- [ ] Define limits and back-pressure strategy for the communication queue in daemon/runtime flow.

## P2 - Next Refactoring Stage

### Service Layer Extraction

- [ ] Extract query and decision logic from threaded module classes into dedicated service objects.
- [ ] Isolate message-building logic from data-fetching logic.
- [ ] Introduce service-layer boundaries between runtime modules and `libs/db_models/`.
- [ ] Reduce direct dependency on concrete ORM models in communication-facing workflows.

### Data Access

- [ ] Introduce repository/query helper layer over direct SQLAlchemy usage.
- [ ] Limit `modules/run/*` access to higher-level data access contracts.
- [ ] Reassess which parts of `libs/db_models.mlms` should become domain adapters instead of direct ORM extensions.

### Tests

- [ ] Prepare regression tests for extracted payment decision paths.
- [ ] Prepare regression tests for extracted tariff validation paths.
- [ ] Prepare regression tests for ICMP incident detection behavior.

## P3 - Structural Cleanup

### Naming And Internal API Cleanup

- [ ] Rename `libs/base/classes.py` mixin classes so their role is explicit and not confused with full base/domain classes.
- [ ] Review whether `libs/db_models.connectors` should stay as a utility helper or become part of a dedicated data-access package.
- [ ] Revisit module discovery conventions driven by `BImporter` and file/class naming assumptions.

### Documentation Follow-Up

- Review generated HTML pages for readability after the docstring normalization pass.
- Decide whether to add separate maintainer-focused pages for `libs/db_models.connectors` and selected ORM aggregates.
- Add explicit cross-links from module guides to generated API entries where useful.
- Consider adding an internal-only Sphinx section for persistence-layer documentation if maintainability requires it.

## Backlog

- [ ] Implement communication failover in `modules/run/mlmspayment.py`.
- [ ] Revisit template-based output opportunities with [Mako Templates](https://docs.makotemplates.org/en/latest/).
