# Welcome to the Acme Team

> **Doc type:** onboarding
> **Audience:** new engineers
> **Owner:** platform-team
> **Depends on:** —
> **Status:** current
> **Last updated:** 2026-01-10

This doc gets you set up as a new engineer working on Acme.

## Day one

1. Get added to the `#acme-eng` and `#acme-oncall` Slack channels.
2. Clone the `acme` monorepo and follow `README.md` to get a local build
   running.
3. Request access to the staging config store — you'll need it to run
   Sapir locally.

## How Acme is organized

Acme is made up of several components that boot in a fixed order: Sapir
loads configuration first, then Nugat and the rest of the core services
start once Sapir confirms configuration is valid. If you're debugging a
startup issue, always check Sapir's logs first — most first-week "Acme
won't start" reports turn out to be a Sapir configuration problem.

## Who to ask

- Config / startup questions → platform-team
- Memory / write-path questions → core-team
- Everything else → post in `#acme-eng`, someone will redirect you
