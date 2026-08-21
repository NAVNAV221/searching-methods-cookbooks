# Kesh — Authentication Errors

> **Component:** Kesh
> **Role:** Authentication and token issuance for Makani
> **Owner:** security-team
> **Depends on:** Sapir
> **Status:** current
> **Last updated:** 2026-07-01

Kesh issues and validates the tokens every other Makani component uses. It
starts immediately after Sapir publishes configuration.

## Error reference

| Log Name                  | Reason                                            | Fix                                            |
| ------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| `KESH_ISSUER_UNREACHABLE` | The configured token issuer did not respond       | Check `makani.auth.issuer_url` and egress rules |
| `KESH_KEY_ROTATION_FAILED`| Signing key rotation did not complete             | Re-run rotation; old key stays valid 24h        |
| `KESH_TOKEN_REJECTED`     | A presented token failed signature validation     | Usually clock skew — check NTP on the caller    |

## Kesh won't start

Kesh has no configuration of its own. It reads `makani.auth.issuer_url` from
the configuration Sapir publishes, so a Kesh that never starts is almost
always a Sapir problem, not a Kesh problem. If Sapir logged a configuration
error, fix that first and Kesh will come up on its own.

If Sapir is healthy and Kesh still won't start, the issuer URL resolved to
something Kesh cannot reach. That surfaces as `KESH_ISSUER_UNREACHABLE`
within about ten seconds of start.

## Impact when Kesh is down

Lomi cannot serve authenticated traffic without Kesh, so the public API
returns 503 across the board. Nugat and Vello are unaffected — they use
internal service identity, not Kesh tokens.

## Key rotation

Rotation runs weekly, automatically. A failed rotation is not urgent: the
previous signing key remains valid for 24 hours, which is the window
security-team uses to intervene during business hours.
