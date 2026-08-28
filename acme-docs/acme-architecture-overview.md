# Acme — Architecture Overview

> **Component:** Platform
> **Role:** How the Acme components fit together
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-06-30

Acme is six services that boot in a fixed order. Nothing starts until the
service it depends on reports healthy, which is why a single failure low in
the chain takes the whole platform down.

## Component dependency table

| Component | Role                          | Depends on   | Owner              |
| --------- | ----------------------------- | ------------ | ------------------ |
| Sapir     | Startup configuration loader  | —            | platform-team      |
| Kesh      | Authentication and tokens     | Sapir        | security-team      |
| Nugat     | Core memory-write engine      | Sapir        | core-team          |
| Vello     | Metrics and telemetry         | Nugat        | observability-team |
| Lomi      | Public API gateway            | Nugat, Kesh  | edge-team          |
| Tuki      | Background job scheduler      | Lomi         | core-team          |

## Boot order

Sapir goes first, always. It loads and validates configuration for every
other component, so if Sapir cannot start, nothing downstream is even
attempted. Kesh and Nugat come up next, in parallel. Vello and Lomi wait for
Nugat, and Lomi additionally waits for Kesh to be issuing tokens. Tuki is
last, because it drives work through Lomi's public API.

## Blast radius

A Sapir outage is a total outage — all five downstream components stay dark.
A Nugat outage takes Vello, Lomi, and Tuki with it, but Kesh keeps serving
tokens. A Lomi outage stops Tuki only. Vello failing affects nothing else;
it is a leaf, which is why Vello alerts are never paged at night.

## Escalation

Page the owning team of the **deepest failed component**, not the one that
alerted. Tuki alerts loudly when Lomi is unavailable, but the Tuki on-call
cannot fix a gateway problem, and the gateway on-call cannot fix Sapir.
