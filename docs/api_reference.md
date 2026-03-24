# API Reference

This section is generated from the current Python modules selected as the
public runtime and plugin-host surface of the project.

## Scope Policy

The generated API reference intentionally includes:

- daemon orchestration,
- shared runtime contracts,
- message and utility helpers used by plugins,
- plugin runtime and configuration helpers.

The generated API reference intentionally excludes archived implementation
trees such as `archive/libs/db_models`. Those files are preserved for
historical reference, not as active runtime API.

```{eval-rst}
.. autosummary::
   :toctree: _generated
   :recursive:

   server.daemon
   libs.app
   libs.conf
   libs.base.classes
   libs.com.message
   libs.tools.datetool
   libs.tools.icmp
   libs.plugins.runtime
   libs.plugins.mixins
   libs.plugins.loader
   libs.plugins.config
   libs.plugins.keys
   libs.plugins.service
   libs.templates.schema
```
