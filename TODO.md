# TODO

## Documentation

- Normalize docstrings in `libs/base/classes.py`, `libs/conf.py`, `libs/com/message.py`, and `server/daemon.py`.
- Align all module docstrings with the current project template and section rules.
- Expand Sphinx autodoc coverage for the most important business modules and helpers.
- Add dedicated API pages for `mlmspayment`, `mlmstariff`, `mzfssnapshot`, and `memailalert`.
- Review and update installation/operations documentation after the documentation toolchain stabilizes.
- Decide whether SQLAlchemy model documentation should be generated in full or kept out of the public API reference.

## Refactoring Preparation

- Extract business rules from threaded module classes into smaller service objects.
- Reduce direct coupling between runtime threads and SQLAlchemy query code.
- Define stable runtime contracts for module inputs, outputs, and message payloads.

## Runtime And Functional Work

### [init config]

if the configuration file does not exist, running the command with the -U flag incorrectly creates a duplicate copy of the description in each section.

### [templates with Mako]

[Mako Templates](https://docs.makotemplates.org/en/latest/)

### [daemon]

limits for communication queue

### [mlmspayment]

implement communication failover
