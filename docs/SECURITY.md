# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 4.x     | ✅ Current         |
| 3.x     | ❌ Deprecated      |

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainers directly
3. Include detailed description and steps to reproduce
4. Allow time for us to investigate and patch

We take security seriously and will respond promptly.

## Security Measures

- API keys stored in environment variables (never in code)
- Google's native content filtering enabled
- No PII stored in sessions
- HTTPS enforced in production (Cloud Run)
- Regular dependency updates
