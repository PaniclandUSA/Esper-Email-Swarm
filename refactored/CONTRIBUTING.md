# Contributing to ESPER Email Swarm

Thank you for your interest in contributing! This project is part of the literacy liberation mission, and we welcome contributions that help make semantic AI more accessible and useful.

## Code of Conduct

Be kind, respectful, and constructive. This is a labor of love. ❤️

## Ways to Contribute

### 1. Code Contributions

**Areas where we need help:**
- Additional semantic agents (spam detection, project clustering, sentiment analysis)
- Email service integrations (Gmail API, Outlook, Exchange)
- UI/UX improvements (web dashboard, mobile apps)
- Performance optimizations
- Bug fixes

**Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass (`pytest`)
6. Format code (`black esper_email_swarm tests`)
7. Commit with clear messages
8. Push and create a Pull Request

### 2. Documentation

- Improve existing documentation
- Add usage examples
- Create tutorials or blog posts
- Translate documentation to other languages
- Write case studies

### 3. Testing

- Test with different email providers
- Report edge cases or bugs
- Add test cases for uncovered scenarios
- Validate routing accuracy with real emails

### 4. Feature Requests

Open an issue with:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Esper-Email-Swarm.git
cd Esper-Email-Swarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=esper_email_swarm --cov-report=html
```

## Code Style

We use:
- **Black** for code formatting (line length: 100)
- **MyPy** for type checking
- **Ruff** for linting
- **Pytest** for testing

Run before committing:
```bash
black esper_email_swarm tests
mypy esper_email_swarm
ruff check esper_email_swarm
pytest
```

## Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Aim for >80% code coverage
- Test both happy paths and edge cases

Example:
```python
def test_urgent_email_routing():
    """Urgent emails should route to 1-URGENT-NOW."""
    text = "URGENT: Please respond ASAP!"
    packets = analyze_email_agents(text)
    metadata = EmailMetadata(sender="test@example.com", subject="URGENT")
    
    analysis = route_email(packets, metadata)
    
    assert analysis.routing_folder == "1-URGENT-NOW"
    assert analysis.urgency > 0.7
```

## Adding a New Agent

To add a new semantic agent:

1. **Define the agent in `agents.py`:**

```python
def _analyze_priority(text: str) -> tuple[float, str]:
    """Detect email priority signals."""
    # Your detection logic here
    priority_score = calculate_priority(text)
    gloss = f"Priority level: {priority_score:.2f}"
    return priority_score, gloss
```

2. **Add to the agent swarm:**

```python
def analyze_email_agents(full_text: str, ...) -> Dict[str, VSEPacket]:
    # ... existing code ...
    
    priority_score, priority_gloss = _analyze_priority(text_lower)
    
    packets["priority"] = VSEPacket(
        agent_role="priority",
        intent_spine=IntentSpine(...),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"priority:{priority_score}:{full_text}"),
        gloss=priority_gloss,
        confidence=0.90,
    )
    
    return packets
```

3. **Update routing logic if needed** in `router.py`

4. **Write tests** in `tests/test_agents.py`:

```python
def test_priority_detection():
    """Test priority agent."""
    text = "High priority request"
    packets = analyze_email_agents(text)
    
    assert "priority" in packets
    assert packets["priority"].intent_spine...
```

## Pull Request Guidelines

**Good PRs:**
- ✅ Focus on a single feature/fix
- ✅ Include tests
- ✅ Update documentation
- ✅ Pass all CI checks
- ✅ Have clear commit messages
- ✅ Reference related issues

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (black)
- [ ] All tests pass
- [ ] No breaking changes (or documented)
```

## Commit Message Format

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

Examples:
- `feat(agents): add spam detection agent`
- `fix(router): correct benevolence clamp threshold`
- `docs(readme): update installation instructions`

## Reporting Bugs

Open an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (Python version, OS)
- Relevant logs or error messages

## Suggesting Enhancements

Open an issue with:
- Clear description of the enhancement
- Motivation and use cases
- Proposed implementation (optional)
- Examples of similar features elsewhere (optional)

## Questions?

- Open a GitHub Discussion
- Email: john@pictogram.org
- Check existing issues and discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- CHANGELOG.md
- GitHub contributors page
- Project documentation (for significant contributions)

---

**Thank you for contributing to literacy liberation!** 🚀

Every improvement to ESPER helps us build better semantic AI systems for education and human comprehension.
