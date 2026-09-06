# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in JapJap, please **do not** open a
public issue. Instead, report it privately by opening a
[GitHub Security Advisory](../../security/advisories/new) on this repository.

Please include:

* A description of the vulnerability and its potential impact
* Steps to reproduce it
* Any relevant logs, code, or configuration (with secrets redacted)

We aim to acknowledge reports within a reasonable timeframe and will work with
you to understand and address the issue before any public disclosure.

## Secrets and API Keys

JapJap is an open-source project. The repository must never contain:

* Real API keys (Gemini, STT providers, etc.)
* Database credentials or connection strings with credentials
* JWT secrets
* Passwords or personal access tokens
* Private certificates or personal information

All configuration is provided via environment variables, documented as
placeholders in [`.env.example`](.env.example). Real values belong only in a
local, git-ignored `.env` file or in your deployment platform's secret
manager — never in source code, commit messages, logs, or documentation.

If you ever find a secret committed to this repository, please report it
using the process above so it can be revoked and removed.

## Supported Versions

JapJap is under active early development. Security fixes are applied to the
`main` branch only until a formal release/versioning process is established.
