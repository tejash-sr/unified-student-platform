# Security Policy

## Reporting a Vulnerability

**Do not** create a public issue for security vulnerabilities. Instead, please email security concerns to the project maintainers.

We appreciate your discretion and will work with you to resolve the issue as quickly as possible.

## Security Practices

### Authentication & Authorization
- JWT tokens with 30-minute expiry
- Refresh tokens with 7-day expiry
- bcrypt password hashing (cost factor: 12)
- All protected endpoints require authentication

### Data Protection
- Database connections use SSL/TLS
- Environment variables stored securely
- No sensitive data in logs
- SQL injection protection via SQLAlchemy ORM
- CSRF protection enabled

### API Security
- CORS configured with specific origins
- Rate limiting on sensitive endpoints
- Input validation on all endpoints
- Output encoding for XSS prevention
- Security headers configured

### Infrastructure
- No secrets in git history
- `.env` file never committed
- Docker images use minimal base images
- Regular dependency updates
- Automated security scanning

### Code Security
- Type checking with TypeScript
- Static analysis with pylint
- OWASP guidelines followed
- Regular code reviews
- Dependency vulnerability scanning

## Security Checklist

- [x] No hardcoded credentials
- [x] Environment variables used for secrets
- [x] Password hashing implemented
- [x] SQL injection prevention (ORM)
- [x] XSS protection
- [x] CSRF protection
- [x] CORS configured
- [x] Rate limiting ready
- [x] Logging implemented
- [x] Error handling without info leakage

## Updates & Patches

- Critical security patches: Emergency release
- High priority patches: Weekly release
- Regular updates: Monthly dependency updates

## Supported Versions

| Version | Status |
|---------|--------|
| 1.x | ✅ Supported |
| < 1.0 | ❌ Not supported |

## Third-Party Dependencies

Dependencies are regularly updated and scanned for vulnerabilities using:
- `npm audit` for frontend/mobile
- `safety` for Python backend
- GitHub Dependabot alerts

---

Thank you for helping keep our project secure!
