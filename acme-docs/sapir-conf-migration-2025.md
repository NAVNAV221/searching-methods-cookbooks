# Sapir — Migrating off `sapir.conf` (2025)

> **Component:** Sapir
> **Role:** Startup configuration loader for Acme
> **Owner:** platform-team
> **Depends on:** —
> **Status:** superseded — migration completed 2025-09
> **Last updated:** 2025-02-11

> **Note:** this page guided the 2025 migration from the flat `sapir.conf`
> file to `acme.config.yaml` and the remote config store. The migration is
> finished; the page is kept for historical reference only.

## What changed

Before the migration, Sapir read a single flat `sapir.conf` file with a
`[required]` section. After it, Sapir resolves each key independently from
`acme.config.yaml`, the process environment, or the remote config store.

The `sapir --reload-config` flag was removed as part of this work. Live
configuration reload no longer exists; Sapir re-validates on every boot and
a restart is the supported path.

## Migration steps (historical)

1. Run `sapir migrate-conf` to emit a `acme.config.yaml` from the existing
   `sapir.conf`.
2. Diff the generated file against `sapir.conf` and confirm every key in the
   `[required]` section is present.
3. Deploy the new file alongside the old one; Sapir preferred the YAML file
   when both were present.
4. Remove `sapir.conf` after one full release cycle.

## Errors during migration

A key present in `sapir.conf` but absent from the generated YAML produced
`CONFIGURATION_IS_MISSING` on the next restart. The fix at the time was to
re-run `sapir migrate-conf`. On current releases this error means something
different — see the current Sapir configuration error guide.
