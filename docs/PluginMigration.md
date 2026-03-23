# Plugin Migration Plan

**Source:** `docs/PluginMigration.md`

**Purpose:**
Define the repository-level migration path from the legacy module runtime to the
new plugin-only architecture.

## Target Result

After migration:

- the daemon loads runtime extensions only from `plugins_dir`,
- the daemon no longer starts `modules.com/*` or `modules.run/*`,
- the legacy runtime tree exists only in `archive/`,
- historical data-model definitions exist only in `archive/libs/db_models/`,
- all new business functionality is implemented as plugins using `Plugin API v1`.

## Active Code To Replace

The following active areas are part of the legacy runtime path and must be
rewritten, removed, or archived:

- `server/daemon.py`
  Current startup logic directly starts legacy communication and worker modules.
- `libs/conf.py`
  Current config generation scans `modules.com` and `modules.run`.
- `libs/base/classes.py`
  `ImporterMixin` currently encodes the legacy file-path and class-name loading convention.
- `libs/interfaces/modules.py`
  The current interface describes the old module contract and should be replaced by plugin-facing runtime interfaces.
- `modules/com/*`
- `modules/run/*`

## Shared Infrastructure Candidates For Reuse

These components appear reusable if decoupled from legacy assumptions:

- `libs.app`
- parts of `libs.base`
- `libs.templates`
- `libs.com.message`
- dispatcher logic
- selected utilities from `libs.tools`

Reuse is acceptable only if the retained code does not preserve the old
`modules.*` loading semantics in the active path.

`TemplateConfigItem` should not remain the public plugin API contract. If it is
retained at all, it should exist only as an internal rendering helper behind
the new schema-based API.

## Proposed Archive Layout

```text
archive/
  modules/
    com/
    run/
  legacy_runtime/
    server/
    libs/
```

Rules:

- preserve historical structure where useful for reference,
- do not import from `archive/` in active runtime code,
- document clearly that `archive/` is non-runtime reference material.

## Replacement Work Packages

### WP1: Plugin Contracts

- add plugin manifest and context objects,
- add runtime protocol,
- add plugin kind enumeration or constants.
- add `PluginConfigField` and `PluginConfigSchema` as the new public
  configuration contract.

### WP2: Plugin Discovery

- scan `plugins_dir`,
- resolve plugin instances by directory entry,
- load `load.py`,
- validate returned `PluginSpec`.

### WP3: Plugin Configuration

- generate per-instance config sections,
- append missing instance variables,
- preserve existing user values,
- render INI output from `PluginConfigSchema`,
- validate parsed config values against `PluginConfigSchema`,
- stop generating sections for legacy modules.

### WP4: Dispatcher Integration

- expose dispatcher methods through plugin-facing context,
- support worker publishing,
- support communication consumer registration.

### WP5: Legacy Removal

- remove legacy startup path from daemon,
- archive legacy modules and loader code,
- delete active references to `modules.com` and `modules.run`.

### WP6: Example Plugins

- `example1`: startup message emitter,
- `example2`: stdout consumer,
- both configured only through user-defined channel mappings.

## Test Plan

- plugin discovery from normal directories,
- plugin discovery from symbolic links,
- invalid `load.py` handling,
- invalid `PluginSpec` handling,
- invalid `PluginConfigSchema` handling,
- config auto-generation for new plugin instances,
- config stability for existing instance sections,
- parsed config validation against schema definitions,
- dispatcher routing only when channel configuration matches,
- no implicit delivery when channel configuration does not match.
