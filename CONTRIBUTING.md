# Contributing to Azure Functions Practical Guide

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Use GitHub Issues for bugs, questions, or suggestions.
- Include reproduction steps when reporting bugs.
- Tag issues appropriately (documentation, bug, enhancement).

### Submitting Changes
1. Fork the repository.
2. Create a branch: `feature/your-change-description`.
3. Make your changes — guide content, troubleshooting playbooks, lab guides, or language tutorials.
4. Test with `mkdocs build --strict` before submitting.
5. Submit a Pull Request.

### Documentation Standards
- All CLI examples must use long flags (`--resource-group`, not `-g`).
- All documents should include Mermaid diagrams where applicable.
- All content must reference Microsoft Learn with source URLs.
- No PII (subscription IDs, tenant IDs, etc.) in CLI output examples.
- Use 4-space indentation for nested lists and admonitions.

### Code Standards
- Shell scripts: Use `set -e`, quote variables.
- Python: Follow PEP 8, include type hints.
- Infrastructure: Use Bicep over ARM templates.

## Review Process
1. Automated CI checks (MkDocs build).
2. Maintainer review for accuracy and completeness.
3. Merge to main triggers deployment.

## Code of Conduct
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
