# Nugat — Write Path Errors

> **Component:** Nugat
> **Role:** Core memory-write engine for Acme
> **Owner:** core-team
> **Depends on:** Sapir
> **Status:** current
> **Last updated:** 2026-03-30

Errors Nugat emits once it is running. For tuning the buffer, see the Nugat
memory-tuning guide instead.

## Error reference

| Log Name                  | Reason                                          | Fix                                        |
| ------------------------- | ----------------------------------------------- | ------------------------------------------ |
| `NUGAT_FLUSH_FAILED`      | A buffer flush did not reach durable storage    | Check `acme.db.host` reachability        |
| `NUGAT_BUFFER_PRESSURE`   | Buffer above the compaction threshold           | Warning only; tune buffer if sustained     |
| `NUGAT_REPLICA_DIVERGED`  | Primary and replica disagree on the write log   | Stop writes and page core-team             |
| `NUGAT_WRITE_REJECTED`    | A write failed validation before buffering      | Caller bug; the payload is logged          |

## Nugat won't start

Nugat has no independent configuration path — every value it uses arrives
from Sapir. A Nugat that never starts means Sapir never published, and the
Sapir logs hold the actual reason. Nugat will not log anything useful in
this case because it never reached its own startup code.

This is the most common false trail during a platform outage: Nugat is
silent, so it looks like the failure, when in fact it was never given the
chance to start.

## Replica divergence

`NUGAT_REPLICA_DIVERGED` is the only Nugat error that is an emergency.
Divergence means the write log is no longer authoritative and continuing to
accept writes compounds the damage. Stop the write path first, page
core-team second, investigate third.

## Durability guarantees

A write is durable once flushed. Buffered writes are not durable, which is
why the flush interval is a durability knob and not only a latency one.
