# Sapir — Configuration Errors (legacy)

> **Component:** Sapir
> **Role:** Startup configuration loader for Acme
> **Owner:** platform-team
> **Depends on:** —
> **Status:** superseded — see sapir-config-errors.md
> **Last updated:** 2024-03-08

> **Note:** this page describes the Sapir error format used before the
> 2025 config-store migration. It's kept for historical reference.

Sapir is the service that loads Acme's configuration at startup. This
page documents `CONFIGURATION_IS_MISSING`, the error Acme operators most
often ask about, as it worked on older Acme releases.

## CONFIGURATION_IS_MISSING

Sapir logs `CONFIGURATION_IS_MISSING` when a required configuration key
for Acme is missing from `sapir.conf`. Acme will not start while this
configuration error is present.

**What to do:**

1. Open `sapir.conf` and check the `[required]` section for the missing
   configuration key.
2. Add the missing configuration key manually to `sapir.conf`.
3. Run `sapir --reload-config` (this flag was removed in the 2025
   migration — use a full restart instead on current Acme releases).
4. If `CONFIGURATION_IS_MISSING` persists after restart, page
   platform-team directly about the Acme configuration issue, since the
   old config-reload path is no longer actively monitored.
