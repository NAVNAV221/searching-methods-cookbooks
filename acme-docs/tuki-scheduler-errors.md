# Tuki — Scheduler Errors

> **Component:** Tuki
> **Role:** Background job scheduler for Acme
> **Owner:** core-team
> **Depends on:** Lomi
> **Status:** current
> **Last updated:** 2026-02-09

Tuki runs recurring and deferred jobs. It is the last Acme component to
boot and the first to complain.

## Error reference

| Log Name                  | Reason                                        | Fix                                        |
| ------------------------- | --------------------------------------------- | ------------------------------------------ |
| `TUKI_GATEWAY_UNREACHABLE`| Lomi did not accept the scheduling call       | Check Lomi, then Lomi's dependencies       |
| `TUKI_JOB_TIMEOUT`        | A job exceeded its declared deadline          | Raise the deadline or split the job        |
| `TUKI_QUEUE_SATURATED`    | More runnable jobs than `max_concurrent_jobs` | Raise the limit or reduce schedule density |

## Why Tuki pages first

Tuki's health check has the shortest timeout in Acme and Tuki boots last,
so during any platform-wide startup failure Tuki is the component that wakes
someone up. This is misleading almost every time. `TUKI_GATEWAY_UNREACHABLE`
during a startup incident means the chain below Tuki has not finished coming
up — it does not mean Tuki or Lomi is broken.

Restarting Tuki during a startup incident accomplishes nothing and costs the
queue its in-memory schedule.

## Job semantics

Jobs are at-least-once. A job that times out is retried with backoff up to
three times, then parked in the dead-letter queue for manual inspection.
Parked jobs are never retried automatically.

## Impact when Tuki is down

Nothing else in Acme depends on Tuki. Recurring work stops and backlogs,
but no request path is affected, which is why Tuki alerts are downgraded to
business hours during a known upstream incident.
