# Contributing to Unified Student Platform

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Branch Naming Convention

- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring
- `test/*` - Test additions
- `chore/*` - Maintenance tasks

### Commit Message Format

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(growth-engine): add churn prediction scoring
fix(api): resolve token expiry validation error
docs(readme): update installation instructions
refactor(auth): simplify password validation logic
```

## Pull Request Process

1. Fork the repo and create your branch from `main`
2. Write clean, descriptive commit messages
3. Add tests if adding new features
4. Update documentation
5. Ensure your PR description clearly describes the problem and solution
6. Link any related issues

## Code Standards

### Python (Backend)
- Follow PEP 8
- Use type hints
- Aim for >90% test coverage
- Document all public functions

### TypeScript (Frontend/Mobile)
- Use strict mode
- Keep components small and focused
- Document complex logic
- Use React best practices

### Commit Message Rules

✅ **Good:**
```
feat: add semantic course matching with embeddings
fix: resolve JWT token expiration in refresh endpoint
docs: add deployment guide for Railway
refactor: extract eligibility scoring to separate service
```

❌ **Bad:**
```
fix bug
updated files
changes
WIP
```

## Reporting Bugs

Include:
- Your OS and version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/logs if applicable

## Code Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Performance impact
- Security considerations

## Questions?

Open an issue with the `question` label.

---

**Thank you for contributing!** 🚀
