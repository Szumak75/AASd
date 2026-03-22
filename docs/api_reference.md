# API Reference

This section is generated from the current Python modules selected as the
public runtime and business-logic surface of the project.

## Scope Policy

The generated API reference intentionally includes:

- daemon orchestration,
- shared runtime contracts,
- message and utility helpers used by modules,
- communication modules,
- business-task modules.

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
   libs.templates.modules
   modules.com.memailalert
   modules.com.memailalert2
   modules.run.micmp
   modules.run.mlmspayment
   modules.run.mlmstariff
   modules.run.mzfssnapshot
   modules.run.memailtest
   modules.run.mtest
```
