# Plugin Migration Status

**Source:** `docs/PluginMigration.md`

**Purpose:**
Summarize the completed migration from the legacy module runtime to the active
plugin-based architecture and list the remaining cleanup work.

## Current Result

The migration baseline is already in place:

- the daemon loads runtime extensions only from `plugins_dir`,
- the daemon no longer starts `modules.com/*` or `modules.run/*`,
- the legacy runtime tree exists only in `archive/`,
- historical data-model definitions exist only in `archive/libs/db_models/`,
- all new business functionality should be implemented as plugins using `Plugin API v1`.

## Replaced Active Code

The following areas were part of the legacy runtime path and were replaced,
removed, or archived during migration:

- `server/daemon.py`
  Startup now delegates plugin lifecycle orchestration to the registry service.
- `libs/conf.py`
  Config generation now scans `plugins_dir` and renders per-instance plugin sections.
- `libs/base/classes.py`
  The active base layer now exposes plugin-oriented mixins and config helpers.
- `libs/interfaces/modules.py`
  The legacy interface is no longer part of the active plugin runtime surface.
- `modules/com/*`
- `modules/run/*`

## Shared Infrastructure Candidates For Reuse

These components remain reusable in the active runtime:

- `libs.app`
- parts of `libs.base`
- `libs.templates`
- `libs.com.message`
- dispatcher logic
- selected utilities from `libs.tools`

Reuse remains acceptable only if the retained code does not preserve the old
`modules.*` loading semantics in the active path.

`TemplateConfigItem` should not remain the public plugin API contract. If it is
retained at all, it should exist only as an internal rendering helper behind
the new schema-based API.

## Archive Layout

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

## Implemented Migration Work

### WP1: Plugin Contracts

- implemented plugin manifest and context objects,
- implemented the runtime protocol and lifecycle snapshots,
- implemented plugin kind constants,
- implemented `PluginConfigField` and `PluginConfigSchema` as the public
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

### WP4a: Plugin-Side Notification Scheduling

- retain interval-based and cron-like scheduling helpers in the shared message
  layer,
- expose a plugin-facing `NotificationScheduler` helper,
- keep scheduling decisions outside the daemon supervision path.

### WP5: Legacy Removal

- remove legacy startup path from daemon,
- archive legacy modules and loader code,
- delete active references to `modules.com` and `modules.run`.

### WP6: Example Plugins

- `example1`: startup message emitter,
- `example2`: stdout consumer,
- both configured only through user-defined channel mappings,
- worker-side timing decisions delegated to plugin helpers instead of daemon
  policy.

## Remaining Work

The migration itself is complete enough for the active runtime model. The main
follow-up work is now hardening:

- strengthen plugin API version diagnostics,
- tighten invalid-registration handling,
- expand supervision and shutdown coverage,
- keep public API documents synchronized with implementation details,
- continue removing historical terminology from active docs.

## Test Coverage

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
