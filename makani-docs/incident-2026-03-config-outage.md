# Incident 2026-03-11 — Platform-wide outage from a missing config key

> **Component:** Platform
> **Role:** Postmortem
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-03-12

A four-hour total outage caused by one unset environment variable.

## Summary

At 02:14 UTC a routine deploy shipped a Sapir release that added a new
required key, `makani.db.replica_host`. The key was set in staging and never
added to production. Sapir logged `CONFIGURATION_IS_MISSING` and refused to
publish configuration. Kesh, Nugat, Vello, Lomi and Tuki never started.

## Timeline

- **02:14** — deploy completes, Sapir restarts and fails the required-key sweep.
- **02:15** — Tuki pages on-call. Tuki is the loudest alert because it is the
  last component to boot and its health check has the shortest timeout.
- **02:15–03:40** — on-call debugs Tuki, then Lomi, then Nugat, working
  upward through the dependency chain one component at a time.
- **03:40** — on-call reads Sapir's logs for the first time and finds the
  missing key named on the line immediately above the error.
- **04:05** — key set, Sapir restarted, platform recovers in order.

## Root cause

The required-keys list is part of the Sapir release; the values are not.
Nothing failed the deploy when the two disagreed.

## What went wrong in the response

Ninety minutes were spent debugging components that were never broken. The
alert that fired was from the component furthest from the fault. Our triage
guidance now says to check Sapir first for any total startup failure.

## Action items

- Deploy gate that diffs the required-keys list against the target
  environment before shipping. **Done, 2026-04.**
- Suppress downstream health-check pages when Sapir is unhealthy. **Done.**
- Add the missing-key name to the alert payload itself. **Open.**
