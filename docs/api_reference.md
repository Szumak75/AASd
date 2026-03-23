# API Reference

This section is generated from the current Python modules selected as the
public runtime and business-logic surface of the project.

## Scope Policy

The generated API reference intentionally includes:

- daemon orchestration,
- shared runtime contracts,
- message and utility helpers used by plugins,
- plugin runtime and configuration helpers.

The generated API reference intentionally excludes most of `libs.db_models.*`.
That package is treated as an internal persistence and integration layer. It is
documented through source docstrings for maintainers, but it is not currently
considered part of the public project API.

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
   libs.plugins.loader
   libs.plugins.config
   libs.templates.schema
```
