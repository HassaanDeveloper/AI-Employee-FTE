# Contributing to AI Employee FTE

Thank you for your interest in contributing to AI Employee FTE! This document provides guidelines and instructions for contributing.

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Clear title and description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)

**Example:**
```markdown
**Bug Summary**
Gmail Watcher fails to connect after token refresh

**Steps to Reproduce**
1. Run gmail_watcher.py
2. Wait for token refresh
3. See error

**Expected:** Token should refresh automatically
**Actual:** Connection fails with 401 error

**Environment:**
- OS: Windows 11
- Python: 3.13
- Version: Gold Tier
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- Use case description
- Proposed solution
- Alternative solutions considered

### Pull Requests

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if applicable)
5. Commit with clear messages
6. Push to your branch
7. Open a Pull Request

## 📝 Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

**Example:**
```python
def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
    """
    Create action file for a Gmail message.
    
    Args:
        message: Gmail message dictionary with 'id' key
        
    Returns:
        Path to created file, or None if failed
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        self.logger.error(f"Error creating action file: {e}")
        return None
```

### Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/config changes

**Examples:**
```bash
feat: Add LinkedIn Watcher for monitoring notifications
fix: Handle UTF-8 encoding in email body extraction
docs: Update README with Platinum Tier deployment guide
refactor: Extract base watcher class for code reuse
```

## 🏗 Architecture Guidelines

### Watcher Pattern

All watchers should inherit from `BaseWatcher`:

```python
class BaseWatcher(ABC):
    @abstractmethod
    def check_for_updates(self) -> list:
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass
```

### MCP Servers

MCP servers should:
- Run on designated ports (Email: 8765, Facebook: 8771, Odoo: 8770)
- Use JSON-RPC 2.0 protocol
- Handle errors gracefully
- Log all operations

### Security

- **NEVER** commit credentials or tokens
- Store secrets in `.secrets/` folder
- Use environment variables for sensitive data
- Follow principle of least privilege

## 🧪 Testing

Before submitting PR:

1. Test all affected components
2. Verify no secrets are committed
3. Check code style (PEP 8)
4. Update documentation if needed

## 📚 Documentation

When adding features:

1. Update README.md
2. Add usage examples
3. Update tier documentation
4. Add inline code comments

## 🎖 Tier Structure

Contributions should align with tier structure:

- **Bronze:** Basic watchers and orchestration
- **Silver:** MCP servers and scheduling
- **Gold:** Odoo integration and advanced features
- **Platinum:** Cloud deployment and sync

## 🚀 Release Process

Releases follow semantic versioning:

- `MAJOR.MINOR.PATCH` (e.g., 1.0.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## 💬 Communication

- Use GitHub Issues for bug reports and feature requests
- Use Pull Requests for code contributions
- Be respectful and constructive in discussions

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI Employee FTE! 🎉
