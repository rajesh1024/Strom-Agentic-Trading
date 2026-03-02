# Contributing to Strom

First off, thank you for considering contributing to Strom! It's people like you that make Strom such a great tool.

## Code of Conduct

All contributors are expected to follow our Code of Conduct. [Insert link or text here].

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please create an issue with:
- A clear title and description.
- Steps to reproduce.
- Expected vs Actual behavior.
- Environment details (OS, Python version, etc.).

### Suggesting Enhancements
Feature requests are welcome! Please open an issue and describe:
- The problem you're trying to solve.
- Your proposed solution.
- Potential alternatives.

### Pull Requests

1. **Branching**: Create a branch from `main` using the format `workstream/T-task-id-short-description`.
   - Workstreams: `backend`, `frontend`, `devops`, `qa`, `docs`.
   - Example: `backend/B1-project-scaffold`
2. **Development**:
   - Write clean, documented code following the patterns in `RULES.md`.
   - Ensure unit tests are added (aim for ≥80% coverage).
   - Run linting and type checking (details in `WORKFLOW.md`).
3. **Submission**:
   - Push your branch and open a PR against `main`.
   - Fill out the PR template below.
4. **Review**:
   - At least one approval is required.
   - Address any reviewer comments.
5. **Merge**:
   - Once approved and CI is green, the PR can be squash-merged.

## Pull Request Template

```markdown
## Task: [Task ID] - [Title]
## Workstream: Backend / Frontend / QA / DevOps / Docs

### What changed
- [bullet list of changes]

### How to test
- [manual test steps if applicable]

### Checklist
- [ ] Unit tests added (≥80% coverage on new code)
- [ ] No lint/type errors
- [ ] Documentation updated (if API/schema changed)
- [ ] No credentials in code
- [ ] Error handling follows RULES.md patterns
```

## Development Setup

See [WORKFLOW.md](.agent/WORKFLOW.md) for detailed setup instructions.
