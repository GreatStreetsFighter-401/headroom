# Security Policy

## Reporting a vulnerability

If you discover a security issue in this project, please report it privately rather than opening a public issue. Use GitHub's **Private vulnerability reporting** (the "Report a vulnerability" button under the repository's Security tab).

Please include enough detail to reproduce the issue. We will acknowledge the report and respond as the challenge timeline allows.

## Handling of secrets

This repository has secret scanning and push protection enabled. The tool needs no credential to run; the one optional key (`CENSUS_API_KEY`, see `.env.example`) is read from the environment and never committed. If a credential is ever committed, it must be rotated (invalidated) immediately — removing it from history alone is not sufficient once it has been pushed.

## What the tool does at run time

Headroom makes outbound HTTPS requests only to the public data sources listed in `docs/DATA_PROVENANCE.md`, writes only under `cache/`, `out/`, `docs/generated/` and `site/data/`, and serves the static page on localhost when asked. It runs no code from the data it downloads.
