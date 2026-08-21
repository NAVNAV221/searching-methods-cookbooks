# Welcome to the Makani Team

> **Doc type:** onboarding
> **Audience:** new engineers
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-01-10

This doc gets you set up as a new engineer working on Makani.

## Day one

1. Get added to the `#makani-eng` and `#makani-oncall` Slack channels.
2. Clone the `makani` monorepo and follow `README.md` to get a local build
   running.
3. Request access to the staging config store — you'll need it to run
   Sapir locally.

## How Makani is organized

Makani is made up of several components that boot in a fixed order: Sapir
loads configuration first, then Nugat and the rest of the core services
start once Sapir confirms configuration is valid. If you're debugging a
startup issue, always check Sapir's logs first — most first-week "Makani
won't start" reports turn out to be a Sapir configuration problem.

## Who to ask

- Config / startup questions → platform-team
- Memory / write-path questions → core-team
- Everything else → post in `#makani-eng`, someone will redirect you
