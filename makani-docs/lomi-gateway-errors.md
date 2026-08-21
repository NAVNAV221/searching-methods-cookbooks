# Lomi — Gateway Errors

> **Component:** Lomi
> **Role:** Public API gateway for Makani
> **Owner:** edge-team
> **Depends on:** Nugat, Kesh
> **Status:** current
> **Last updated:** 2026-06-02

Lomi terminates public traffic and is the only Makani component exposed to
the internet. It waits for both Nugat and Kesh before accepting connections.

## Error reference

| Log Name                     | Reason                                           | Fix                                           |
| ---------------------------- | ------------------------------------------------ | --------------------------------------------- |
| `LOMI_UPSTREAM_UNAVAILABLE`  | Nugat did not answer a write within the deadline | Check Nugat health before touching Lomi       |
| `LOMI_AUTH_BACKEND_DOWN`     | Kesh is not issuing tokens                       | Check Kesh; Lomi recovers on its own          |
| `LOMI_PORT_BIND_FAILED`      | `makani.gateway.public_port` already in use      | Another process holds the port                |
| `LOMI_REQUEST_TOO_LARGE`     | Body exceeded the configured limit               | Client-side; raise the limit only deliberately |

## Reading Lomi errors correctly

Lomi is the most alerted-on component in Makani and the least often at
fault. It sits above two dependencies, so almost every Lomi error is a
faithful report of somebody else's outage. `LOMI_UPSTREAM_UNAVAILABLE` and
`LOMI_AUTH_BACKEND_DOWN` in particular should be read as "Nugat is down" and
"Kesh is down" respectively.

Genuine Lomi faults are the two configuration errors: a port collision, or a
request-size limit set wrong. Both surface within seconds of start and neither
is affected by upstream health.

## Impact when Lomi is down

All public API traffic stops, and Tuki stops making progress because it
drives its work through Lomi. Internal writes through Nugat continue.

## Draining safely

Lomi drains in-flight requests for 30 seconds on `SIGTERM`. Never `SIGKILL`
a Lomi instance carrying traffic — in-flight writes will have reached Nugat
without the client learning the outcome.
