# Contributing to Azure PaaS Troubleshooting Labs

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Use GitHub Issues for bugs, questions, or suggestions.
- Include reproduction steps when reporting bugs.
- Tag issues appropriately (experiment, documentation, infrastructure).

### Submitting Experiments
1. Fork the repository.
2. Create a branch: `experiment/your-experiment-name`.
3. Follow the [experiment template](experiments/templates/experiment-template.md).
4. Include:
    - Complete 16-section documentation.
    - Reproduction scripts (if applicable).
    - Evidence-tagged conclusions.
5. Submit a Pull Request.

### Documentation Standards
- Use the canonical templates in `experiments/templates/`.
- Follow [Evidence Levels](docs/methodology/evidence-levels.md) for conclusions.
- Include KQL queries where applicable.
- Test with `mkdocs build --strict` before submitting.

### Code Standards
- Shell scripts: Use `set -e`, quote variables.
- Python: Follow PEP 8, include type hints.
- Infrastructure: Use Bicep over ARM.

## Review Process
1. Automated CI checks (MkDocs build, linting).
2. Maintainer review for accuracy and completeness.
3. Merge to main triggers deployment.

## Code of Conduct
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
