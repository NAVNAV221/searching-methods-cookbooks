# Vello — Metrics Pipeline

> **Component:** Vello
> **Role:** Metrics and telemetry for Acme
> **Owner:** observability-team
> **Depends on:** Nugat
> **Status:** current
> **Last updated:** 2026-05-20

Vello collects metrics from every Acme component and ships them to the
configured sink. It reads Nugat's write stream, so it starts after Nugat.

## Error reference

| Log Name                | Reason                                       | Fix                                          |
| ----------------------- | -------------------------------------------- | -------------------------------------------- |
| `VELLO_SINK_REJECTED`   | The telemetry sink refused a batch           | Check sink credentials and quota             |
| `VELLO_STREAM_LAGGING`  | Vello is behind Nugat's write stream         | Usually transient; sustained lag means resize |
| `VELLO_CARDINALITY_CAP` | A metric exceeded its label-cardinality cap  | Fix the emitting component, not Vello        |

## Vello is a leaf

Nothing in Acme depends on Vello. If Vello is down you lose visibility,
not function — which is exactly when you most want it back, and also why
Vello is never paged overnight. Metrics gaps during an incident are expected
and are not themselves an incident.

## Reading metrics during a startup failure

During a Sapir configuration failure, Vello never starts, so there are no
metrics for the outage at all. This is the single most common complaint after
a platform-wide startup incident: the dashboards are empty precisely for the
window you want to investigate. Use component logs, not dashboards, for
startup failures.

## Cardinality

The label-cardinality cap exists to stop one component from evicting
everyone else's metrics. Raising it is almost never the right fix; the
emitting component is usually putting a request ID in a label.
