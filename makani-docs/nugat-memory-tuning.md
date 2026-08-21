# Nugat — Memory Buffer Configuration Guide

> **Component:** Nugat
> **Role:** Core memory-write engine for Makani
> **Owner:** core-team
> **Depends on:** Sapir
> **Status:** current
> **Last updated:** 2026-05-02

Nugat is the component that writes Makani's in-flight state to persistent
memory. Under heavy write load, the default buffer configuration can cause
latency spikes, so this guide covers how to tune it.

## Configuration parameters

| Parameter                    | Default | What it controls                                        |
| ---------------------------- | ------- | ------------------------------------------------------- |
| `nugat.buffer_size_mb`       | 64      | Size of the in-memory write buffer before a flush       |
| `nugat.flush_interval_ms`    | 500     | Max time between forced flushes                         |
| `nugat.compaction_threshold` | 0.7     | Fraction of buffer usage that triggers early compaction |

## Recommended configuration by workload

- **Bursty write workloads:** increase `buffer_size_mb` to 128–256 and
  raise `flush_interval_ms` to reduce flush frequency.
- **Low-latency workloads:** lower `flush_interval_ms` to 100–200 so
  writes hit disk sooner, at the cost of more frequent flushes.
- **Memory-constrained hosts:** keep `buffer_size_mb` at the default and
  lower `compaction_threshold` instead.

Misconfiguring these values doesn't stop Nugat from starting — it degrades
gracefully and logs `NUGAT_BUFFER_PRESSURE` warnings instead of failing
outright. If Makani is failing to start entirely, the problem is almost
always upstream in Sapir, not here.
