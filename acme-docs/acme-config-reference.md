# Acme — Configuration Key Reference

> **Component:** Platform
> **Role:** Canonical list of Acme configuration keys
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-07-15

Every key Sapir knows about. Required keys must resolve from some source or
startup fails.

## Required keys

| Key                          | Type   | Consumed by | Notes                                  |
| ---------------------------- | ------ | ----------- | -------------------------------------- |
| `acme.db.host`             | string | Nugat       | Primary write target                   |
| `acme.db.replica_host`     | string | Nugat       | Added 2026-03; required since 2026-03  |
| `acme.auth.issuer_url`     | string | Kesh        | Token issuer, must be HTTPS            |
| `acme.gateway.public_port` | int    | Lomi        | Defaults blocked in production         |
| `acme.telemetry.sink`      | string | Vello       | Set to `none` to disable, never unset  |

## Optional keys

| Key                          | Default | Consumed by |
| ---------------------------- | ------- | ----------- |
| `nugat.buffer_size_mb`       | 64      | Nugat       |
| `nugat.flush_interval_ms`    | 500     | Nugat       |
| `lomi.rate_limit_rps`        | 2000    | Lomi        |
| `tuki.max_concurrent_jobs`   | 32      | Tuki        |

## Resolution order

Sapir resolves each key from `acme.config.yaml` first, then the process
environment (uppercased and prefixed, so `acme.db.host` becomes
`ACME_DB_HOST`), then the remote config store. A key that resolves from
none of the three produces `CONFIGURATION_IS_MISSING` and Acme will not
start.

## Adding a required key

Adding to the required-keys list is a breaking change for every environment
that hasn't set a value yet. Ship the value first, the requirement second.
