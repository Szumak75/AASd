# Plugin Author Checklist

**Purpose:**
Provide a practical checklist for implementing new plugins against the current
`Plugin API v1` used by AASd.

## Minimum Structure

- Create one plugin instance directory under `plugins_dir`.
- Expose `load.py` at the plugin root.
- Export `get_plugin_spec() -> PluginSpec`.
- Keep plugin-local helper modules under a plugin-owned subdirectory when the
  implementation grows beyond `load.py`.

## Manifest Checklist

- Set a stable `plugin_id` that identifies the implementation, not the
  instance name.
- Set `plugin_kind` to either `PluginKind.WORKER` or
  `PluginKind.COMMUNICATION`.
- Provide a `PluginConfigSchema` with all instance-local configuration fields.
- Avoid daemon-reserved keys from `PluginHostKeys` in field names and aliases.
- Keep field names and aliases unique inside one schema.

## Runtime Checklist

- Implement `initialize()`, `start()`, `stop()`, `state()`, and `health()`.
- Treat `PluginContext` as the only supported daemon-facing service contract.
- Access application identity through `context.app_meta`.
- Publish worker messages only through `context.dispatcher.publish(...)`.
- Use `NotificationScheduler` when worker notification timing should follow
  shared `message_channel` and `at_channel` semantics.
- Register communication consumers only through
  `context.dispatcher.register_consumer(...)`.
- Do not assume any direct plugin-to-plugin communication path.

## Typing Checklist

- Use private key constants with `ReadOnlyClass` for plugin-specific config
  names.
- Prefer typed mixins such as `ThPluginMixin` for thread-based runtimes.
- Narrow `Optional[...]` values explicitly before using them in methods that
  must return concrete types.
- Return fallback `PluginStateSnapshot` or `PluginHealthSnapshot` objects
  instead of leaking `None` through strongly typed methods.

## State And Health Checklist

- Initialize `_health` with `PluginHealth.UNKNOWN`.
- Initialize `_state` with `PluginState.CREATED`.
- Move to `INITIALIZED` only after internal preparation succeeds.
- Record `FAILED` with a useful `message` when initialization or runtime
  preconditions are missing.
- Keep `state()` and `health()` side-effect free except for lightweight state
  normalization such as `STARTING -> RUNNING`.

## Configuration Checklist

- Use `PluginCommonKeys` for shared names such as `channel`,
  `message_channel`, `at_channel`, and `sleep_period`.
- Use `channel` for communication-plugin consumers and `message_channel` for
  worker-plugin notification targets.
- Use `at_channel` when a worker needs cron-like emission windows.
- Keep plugin-specific secrets and variables inside the plugin schema.
- Treat each config section as one plugin instance.
- Do not infer routing or peers from `plugin_id`, paths, or class names.

## Review Checklist

- `poetry run pytest`
- `make docs` when public API docs changed
- update `CHANGELOG.md`
- update version metadata when code changed

## Reference Implementation

The current reference implementations are:

- `plugins/example1/load.py`
- `plugins/example2/load.py`

They demonstrate:

- local `_Keys` usage,
- `PluginSpec` construction,
- `PluginContext` consumption,
- `ThPluginMixin` for typed runtime storage,
- explicit `Optional[...]` narrowing for runtime internals,
- consistent lifecycle and health snapshot handling.

## Starter Templates

Ready-to-copy starter templates are available under:

- `examples/plugin-worker-template/`
- `examples/plugin-comms-template/`

Use the worker template for producer or task-oriented plugins and the
communication template for plugins that consume dispatcher traffic. In both
cases, replace the placeholder identifiers, config schema, and runtime logic.
