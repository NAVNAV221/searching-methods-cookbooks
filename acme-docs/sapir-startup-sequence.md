# Sapir — Startup Sequence

> **Component:** Sapir
> **Role:** Startup configuration loader for Acme
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-04-22

What Sapir actually does between process start and reporting healthy. Useful
when a boot hangs rather than fails outright.

## The four phases

1. **Discovery** — Sapir enumerates configuration sources in priority order:
   `acme.config.yaml`, then process environment, then the remote config
   store. Sources are read, never merged silently; the first source with a
   value wins and the choice is logged.
2. **Validation** — every discovered value is checked against the schema in
   `sapir/schema.py`. Type errors surface here as
   `CONFIGURATION_IS_INVALID`, never as a runtime failure later.
3. **Required-key sweep** — Sapir walks its required-keys list and confirms
   each one resolved. A miss here is what produces the startup failure the
   platform-team gets paged for.
4. **Publish** — the validated configuration is published to the local
   config socket. Only now do Kesh and Nugat begin their own startup.

## Timing expectations

A healthy Sapir boot completes all four phases in under 800ms. If discovery
alone exceeds two seconds, the remote config store is usually unreachable
and you'll see `CONFIGURATION_SOURCE_UNREACHABLE` shortly after.

## Why Sapir fails fast

Sapir deliberately refuses to start the rest of Acme in a half-configured
state. A partially configured Nugat will accept writes it cannot durably
flush, which is far more expensive to recover from than a clean startup
failure. The tradeoff is that any configuration problem is a total outage.
