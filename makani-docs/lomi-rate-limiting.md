# Lomi — Rate Limiting

> **Component:** Lomi
> **Role:** Public API gateway for Makani
> **Owner:** edge-team
> **Depends on:** Nugat, Kesh
> **Status:** current
> **Last updated:** 2025-11-18

How Lomi sheds load, and how to tune it.

## Configuration

| Parameter                 | Default | What it controls                            |
| ------------------------- | ------- | ------------------------------------------- |
| `lomi.rate_limit_rps`     | 2000    | Sustained requests per second per tenant    |
| `lomi.burst_multiplier`   | 1.5     | Short-term headroom above the sustained rate |
| `lomi.shed_priority`      | `fair`  | `fair` or `strict` — who gets dropped first |

## How limiting works

Lomi uses a token bucket per tenant, refilled at `rate_limit_rps`. A tenant
may briefly exceed its rate up to `rate_limit_rps × burst_multiplier` before
requests are rejected with HTTP 429. Rejections are cheap and never reach
Nugat.

Under `fair` shedding, every tenant over its limit is throttled equally.
Under `strict`, tenants are ranked by contract tier and the lowest tier is
dropped first. Most environments run `fair`; `strict` exists for the managed
offering.

## When to raise the limit

Raise `rate_limit_rps` only after confirming Nugat can absorb the extra
write volume. Lomi will happily forward more traffic than Nugat can flush,
and the failure mode moves from a clean 429 at the edge to buffer pressure
deep in the write path, which is much harder to diagnose.

## What rate limiting will not fix

429s during a startup incident are not a capacity problem. If Nugat is
still coming up, Lomi's limiter is doing its job and tuning it will make
things worse.
