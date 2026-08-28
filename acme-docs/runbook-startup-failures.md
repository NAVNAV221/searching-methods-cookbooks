# Runbook — Acme Won't Start

> **Component:** Platform
> **Role:** First-response runbook for total startup failures
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-04-05

Use this when the platform is down and you don't yet know which component is
at fault. This runbook triages; it does not fix.

## Triage

1. Check whether Sapir reported healthy. If it did not, stop here — nothing
   downstream will start, and every other alert you're seeing is noise.
2. If Sapir is healthy, find the deepest component that is not healthy and
   go to that component's error guide.
3. Only escalate to the team that owns the deepest failed component.

## Common first-response mistakes

- **Restarting the alerting component.** Tuki alerts first because it is
  last to boot, so on-call instinctively restarts Tuki. This never helps.
- **Chasing memory warnings.** Nugat emits buffer-pressure warnings during
  any slow boot. They are a symptom, not a cause.
- **Rolling back the deploy.** If the failure is a missing configuration
  key, a rollback restores the old config and hides the real problem until
  the next deploy.

## If Sapir is the failed component

Sapir failures fall into three buckets, all logged as structured errors:
a missing required key, a value that failed validation, or an unreachable
config store. `CONFIGURATION_IS_MISSING` is by far the most common of the
three. See the Sapir configuration error guide for the fix procedure — do
not attempt to patch configuration by hand from this runbook.

## Escalation path

platform-team owns Sapir and this runbook. If Sapir is healthy and the
failure is downstream, hand off to the owning team from the architecture
overview rather than debugging it yourself.
