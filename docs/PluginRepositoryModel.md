# Plugin Repository Model

**Purpose:**
Describe the recommended way to organize plugins as separate repositories while
keeping them compatible with the active AASd plugin runtime.

## Recommended Model

The recommended default model is:

1. keep each plugin in its own repository,
2. connect plugin instances to AASd through `plugins_dir`,
3. represent runtime instances in `plugins_dir` by directories or symbolic
   links,
4. install plugin runtime dependencies into the same Python environment used by
   AASd.

This matches the active runtime contract:

- AASd discovers plugin instances from `plugins_dir`,
- each directory entry or symlink is one instance,
- instance names are derived from entry names,
- one implementation may be reused by multiple instances.

## Why This Model

This model keeps the daemon and plugin implementation concerns separate:

- AASd remains the runtime host and supervisor,
- plugin code evolves independently,
- plugin repositories can have their own release cycle,
- instance configuration stays in the AASd configuration file,
- one plugin implementation can be mounted more than once through symlinks.

## Recommended Workspace Layout

Typical development workspace:

```text
workspace/
  AASd/
  aasd-plugin-mail/
  aasd-plugin-telegram/
```

Mounted into AASd:

```text
AASd/
  plugins/
    mail_primary -> ../../aasd-plugin-mail
    mail_backup  -> ../../aasd-plugin-mail
    telegram_ops -> ../../aasd-plugin-telegram
```

In this layout:

- `aasd-plugin-mail` is one implementation repository,
- `mail_primary` and `mail_backup` are two runtime instances,
- AASd creates separate config sections for both instances.

## Plugin Repository Layout

Recommended minimal plugin repository:

```text
aasd-plugin-mail/
  load.py
  README.md
  requirements.txt
  plugin/
    __init__.py
    runtime.py
    config.py
  tests/
```

Rules:

- `load.py` is the daemon entry point,
- plugin-specific logic may be moved to subpackages owned by the plugin,
- plugin tests should live in the plugin repository,
- plugin dependencies should be declared by the plugin repository.

## Runtime Integration

The plugin must depend only on the public AASd host API, not on arbitrary
daemon internals.

Safe dependency examples:

- `libs.plugins.runtime`
- `libs.plugins.keys`
- `libs.plugins.mixins`
- `libs.com.message`
- selected public runtime helpers documented in the AASd API guides

Avoid:

- importing archived code,
- depending on implementation details outside the documented runtime API,
- direct plugin-to-plugin imports as a communication mechanism.

## Dependency Management

Plugins run inside the same Python environment as AASd.

That means:

- AASd provides the host runtime and public API,
- the plugin provides its own code and extra dependencies,
- the operator or developer must install plugin dependencies into the same
  environment used to run AASd.

Typical development flow:

```bash
cd /path/to/workspace/AASd
ln -s ../../aasd-plugin-mail plugins/mail_primary
poetry run pip install -r ../aasd-plugin-mail/requirements.txt
poetry run python aasd.py
```

The daemon does not currently manage plugin dependency installation by itself.

## Instance Model

One implementation repository may back multiple daemon instances.

Example:

```text
plugins/
  mail_primary -> ../../aasd-plugin-mail
  mail_backup  -> ../../aasd-plugin-mail
```

Expected config result:

```ini
[mail_primary]
...

[mail_backup]
...
```

This is the preferred way to model:

- multiple destinations,
- different credentials,
- separate routing channels,
- different operational roles using one implementation.

## Versioning And Compatibility

Versioning should be separated into:

- AASd host version,
- plugin implementation version,
- plugin API compatibility version.

Recommended mapping:

- `PluginSpec.api_version` defines compatibility with the daemon host API,
- `PluginSpec.plugin_version` identifies the plugin release,
- AASd versioning remains independent from plugin repository versioning.

This allows a plugin to evolve independently while still declaring explicit
compatibility with the host runtime.

## Development Workflow

Recommended workflow for plugin authors:

1. develop the plugin in its own repository,
2. mount it into AASd with a symlink under `plugins/` or another configured
   `plugins_dir`,
3. install plugin dependencies into the same environment as AASd,
4. test the plugin in its own repository,
5. validate integration by running AASd against the mounted instance.

This keeps repository ownership clear and avoids mixing plugin code directly
into the AASd repository.

## Integration Repository Option

If a deployment or integration workspace needs pinned plugin revisions, use a
separate integration layer with `git submodule`.

Recommended structure:

```text
AASd/
  external/
    aasd-plugin-mail/      # git submodule
  plugins/
    mail_primary -> ../external/aasd-plugin-mail
    mail_backup  -> ../external/aasd-plugin-mail
```

This is useful when:

- exact plugin revisions must be pinned,
- integration environments must be reproducible,
- the plugin still needs to remain an independent repository.

## Why Symlink Plus Submodule Is Better Than Direct Submodule In `plugins/`

Using `external/<plugin>` plus symlinks in `plugins/` is preferred over placing
the submodule directly inside `plugins/`:

- the implementation repository remains mounted once,
- multiple runtime instances stay easy to express,
- instance names remain clean and operationally meaningful,
- repository layout stays consistent between local development and deployment.

## Models To Avoid

Avoid these as the default project model:

- copying plugin source code directly into `plugins/`,
- using `git subtree` to vendor plugin code into AASd,
- treating `plugins/` as a monorepo folder for all implementations,
- coupling plugin routing through imports or shared globals instead of the
  dispatcher and config.

These approaches blur the host/plugin boundary and make independent versioning
harder.

## Recommended Default

The recommended default for this project is:

- plugin implementation in a separate repository,
- plugin instance mounted into `plugins_dir` through a symbolic link,
- optional `git submodule` only in an integration or deployment workspace,
- multiple runtime instances represented by multiple symlinks,
- all runtime dependencies installed into the same Python environment as AASd.

This is the model most aligned with the active AASd architecture and the
current `Plugin API v1`.
