# Contributing to Moldflow API

Thank you for considering contributing to Moldflow API! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/moldflow-api.git`
3. Navigate to the directory: `cd moldflow-api`
4. Install dependencies: `python -m pip install -r requirements.txt`

### Development Workflow

1. Create a new branch for your feature: `git checkout -b feature-name`
2. Make your changes
3. Run tests: `python run.py test`
4. Run linting: `python run.py lint`
5. Run formatting: `python run.py format`
6. Commit your changes: `git commit -m "Add feature"`
7. Push to your fork: `git push origin feature-name`
8. Create a Pull Request

### Code Style

* We use `black` for code formatting
* We use `pylint` for linting
* Pre-commit hooks are configured to run these automatically
* Please ensure your code passes all checks before submitting

### Testing

* Write tests for new functionality
* Ensure all existing tests pass
* Use meaningful test names and descriptions
* Tests should be in the `tests/` directory

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface, if applicable
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent
4. Your Pull Request will be merged once you have the sign-off of at least one maintainer

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Questions?

Feel free to open an issue for any questions about contributing!
