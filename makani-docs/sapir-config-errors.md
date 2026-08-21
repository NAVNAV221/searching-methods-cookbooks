# Sapir — Configuration Errors

> **Component:** Sapir
> **Role:** Startup configuration loader for Makani
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-06-14

Sapir is the service that loads and validates Makani's configuration at
startup, before any other component (including Nugat) is allowed to boot.
If Sapir can't find or parse a required setting, it fails fast and logs a
structured error so the rest of Makani never starts in a half-configured
state.

## Quick reference

| Log Name                           | Reason                                                | Fix |
|-------------------------------------|--------------------------------------------------------|-----|
| `CONFIGURATION_IS_MISSING`          | A required config key or env var was not found         | Set the missing key in `makani.config.yaml` or as an env var, then restart Sapir |
| `CONFIGURATION_IS_INVALID`          | A config value was found but failed schema validation   | Check the value's type/format against the schema in `sapir/schema.py` |
| `CONFIGURATION_SOURCE_UNREACHABLE`  | Sapir couldn't reach the remote config store            | Check network/VPN access to the config store |

## CONFIGURATION_IS_MISSING

This is the most common startup failure reported for Makani. It means Sapir
scanned its required-keys list and found at least one key with no value —
neither in `makani.config.yaml`, nor as an environment variable, nor in the
remote config store.

A typical failure looks like this in the logs:

    2026-08-09T14:32:11.483Z ERROR sapir.startup.ConfigLoader - CONFIGURATION_IS_MISSING: required key 'makani.db.host' not found (attempt 1/3)

The class that raises it is always `ConfigLoader`, and the lookup itself
goes through `get_tool_config`. If your log line comes from anywhere else,
this isn't a Sapir configuration issue.

**What to do:**

1. Look at the log line immediately before `CONFIGURATION_IS_MISSING` —
   Sapir always prints the name of the missing key right above the error.
2. Confirm the key exists in `makani.config.yaml` for your environment.
3. If it's meant to come from an env var, confirm it's actually set in the
   process's environment (`printenv | grep MAKANI_`).
4. Restart Sapir. It re-validates on every boot, so a partial fix is safe
   to retry.

This error is **not** related to Nugat's memory configuration — if you're
seeing memory-tuning warnings instead, see the Nugat memory-tuning guide.
