# Contributing to AI Technical Interviewer

Thank you for your interest in contributing! 🎉

---

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/my-feature`
4. **Make** your changes
5. **Test** your changes: `adk web src`
6. **Commit** with clear messages
7. **Push** to your fork
8. **Open** a Pull Request

---

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-interviewer-google-adk.git
cd ai-interviewer-google-adk
git checkout google-adk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

# Run locally
adk web src
```

---

## Code Style

- **Python 3.11+** required
- Follow **PEP 8** style guidelines
- Use **type hints** where possible
- Write **docstrings** for functions
- Keep functions **small and focused**

---

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add new question generation tool
fix: Resolve session timeout issue
docs: Update deployment instructions
refactor: Simplify agent configuration
```

Prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance

---

## Pull Request Process

1. Ensure your code works locally
2. Update documentation if needed
3. Add tests for new functionality
4. Keep PRs focused and small
5. Describe your changes clearly

---

## Areas for Contribution

- 🐛 Bug fixes
- 📚 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX enhancements
- 🔧 New tools for the agent
- 🌐 Internationalization

---

## Questions?

Open an issue or start a discussion. We're happy to help!

---

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

Thank you for helping improve AI Technical Interviewer! 🙏
