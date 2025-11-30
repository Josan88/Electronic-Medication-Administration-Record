# Contributing to eMAR

Thank you for your interest in contributing to the Electronic Medication Administration Record (eMAR) project! This guide will help you get started with contributing to the codebase.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and considerate in all interactions.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Publishing others' private information
- Trolling, insulting/derogatory comments
- Spam or commercial promotion
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before you begin contributing, make sure you have:

- Python 3.8 or higher installed
- Git installed and configured
- A GitHub account
- Basic knowledge of Flask and REST APIs
- Understanding of the eMAR project (read README.md and ARCHITECTURE.md)

### Finding Issues to Work On

1. **Good First Issues**: Look for issues labeled `good first issue` - these are great for newcomers
2. **Help Wanted**: Issues labeled `help wanted` are ready for community contributions
3. **Documentation**: Documentation improvements are always welcome
4. **Bug Fixes**: Check the issue tracker for bugs that need fixing

### Communication Channels

- **GitHub Issues**: For bug reports, feature requests, and discussions
- **Pull Requests**: For code contributions
- **Documentation**: For questions about the system architecture

---

## Development Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub (click the Fork button)

# Clone your fork
git clone https://github.com/YOUR_USERNAME/Electronic-Medication-Administration-Record.git
cd Electronic-Medication-Administration-Record

# Add upstream remote
git remote add upstream https://github.com/Josan88/Electronic-Medication-Administration-Record.git
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your ThingSpeak API keys
# See DEPLOYMENT.md for setup instructions
```

### 5. Verify Setup

```bash
# Run the application
python app.py

# In another terminal, test the health endpoint
curl http://localhost:5000/api/health

# Access the UI
# Open browser to http://localhost:5000
```

---

## Project Structure

Understanding the project structure is crucial for effective contributions:

```
Electronic-Medication-Administration-Record/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── swagger.yaml               # OpenAPI specification
├── .env                       # Environment variables (not in git)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
│
├── routes/                    # Route blueprints (API endpoints)
│   ├── __init__.py           # Blueprint registration
│   ├── patients.py           # Patient management routes
│   ├── prescriptions.py      # Prescription routes
│   ├── tracking.py           # Medication tracking routes
│   └── queue.py              # Queue management routes
│
├── services/                  # Service layer (business logic)
│   ├── __init__.py
│   ├── thingspeak_service.py # ThingSpeak API integration
│   └── queue_service.py      # Persistent queue management
│
├── validators/                # Input validation layer
│   ├── __init__.py
│   ├── patient_validator.py
│   ├── prescription_validator.py
│   └── tracking_validator.py
│
├── utils/                     # Utility modules
│   ├── errors.py             # Error handling utilities
│   ├── logging_config.py     # Logging configuration
│   └── status_calculator.py  # Status calculation logic
│
├── static/                    # Static files
│   ├── css/
│   │   └── style.css         # Application styles
│   └── js/
│       └── main.js           # Frontend JavaScript
│
├── templates/                 # HTML templates
│   ├── index.html            # Main dashboard
│   ├── role_selection.html   # Landing page
│   ├── nurse_login.html      # Nurse login
│   └── management_login.html # Management login
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md       # System architecture
│   └── DEPLOYMENT.md         # Deployment guide
│
└── tests/                     # Test files
    ├── test_blueprints.py
    ├── test_validation.py
    ├── test_api_validation.py
    ├── test_queue_management.py
    └── test_queue_integration.py
```

### Key Components

- **Routes**: Handle HTTP requests, call validators and services
- **Services**: Contain business logic and external API interactions
- **Validators**: Sanitize and validate input data
- **Utils**: Shared utilities (errors, logging, calculations)

---

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- Features: `feature/feature-name`
- Bug fixes: `fix/bug-description`
- Documentation: `docs/what-you-are-documenting`
- Refactoring: `refactor/what-you-are-refactoring`

### 2. Make Your Changes

Follow these principles when making changes:

- **Keep changes focused**: One feature/fix per branch
- **Write clean code**: Follow the coding standards (see below)
- **Test your changes**: Add tests and verify everything works
- **Document your changes**: Update relevant documentation
- **Commit frequently**: Make small, logical commits

### 3. Commit Your Changes

Write clear, descriptive commit messages:

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add patient search functionality to API"

# Follow this format:
# - Start with a verb (Add, Fix, Update, Remove, etc.)
# - Be concise but descriptive
# - Reference issue numbers if applicable
```

**Good commit messages:**
```
Add patient search endpoint with filtering
Fix rate limit handling in prescription queue
Update API documentation for tracking endpoint
Refactor validation logic to reduce duplication
```

**Bad commit messages:**
```
Update
Fixed bug
Changes
WIP
```

### 4. Push Your Changes

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template (see below)
5. Submit the pull request

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some project-specific conventions:

#### General Rules

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 88 characters (Black formatter default)
- **Imports**: Group by standard library, third-party, local
- **Docstrings**: Use triple quotes for all functions/classes
- **Type hints**: Use where helpful but not required

#### Example

```python
"""
Module docstring explaining the purpose of this module.
"""

from flask import Blueprint, request
from services.thingspeak_service import thingspeak_service
from utils.errors import error_response, success_response, ValidationError
from validators import validate_patient_data


patients_bp = Blueprint('patients', __name__, url_prefix='/api')


@patients_bp.route("/patients", methods=["POST"])
def add_patient():
    """
    Add a new patient to the system.
    
    Validates input data and writes to ThingSpeak patient channel.
    
    Returns:
        JSON response with entry_id and success message
        
    Raises:
        ValidationError: If input data is invalid
        ThingSpeakError: If ThingSpeak API call fails
    """
    try:
        data = request.json
        if data is None:
            raise ValidationError("Invalid JSON data")

        validated_data = validate_patient_data(data)
        entry_id = thingspeak_service.write_to_channel("patient_info", validated_data)
        
        return success_response(
            data={"entry_id": entry_id},
            message="Patient added successfully"
        )
    except ValidationError as e:
        return error_response(str(e), 400)
```

### JavaScript Style Guide

- **Indentation**: 2 spaces
- **Semicolons**: Use them consistently
- **Quotes**: Use double quotes for strings
- **Naming**: camelCase for variables/functions
- **ES6+**: Use modern JavaScript features

#### Example

```javascript
async function addPatient(patientData) {
  try {
    const response = await fetch("/api/patients", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(patientData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error adding patient:", error);
    throw error;
  }
}
```

### Code Organization

#### Route Handlers

```python
@blueprint.route("/endpoint", methods=["GET", "POST"])
def handler():
    """Docstring explaining what this endpoint does."""
    try:
        # 1. Get and validate input
        data = request.json
        validated_data = validator(data)
        
        # 2. Call service layer
        result = service.method(validated_data)
        
        # 3. Return response
        return success_response(data=result)
    except SpecificError as e:
        return error_response(str(e), status_code)
```

#### Service Methods

```python
class ThingSpeakService:
    """Service for interacting with ThingSpeak API."""
    
    def method_name(self, param1, param2):
        """
        Brief description of what this method does.
        
        Args:
            param1: Description of param1
            param2: Description of param2
            
        Returns:
            Description of return value
            
        Raises:
            ThingSpeakError: When API call fails
        """
        try:
            # Implementation
            return result
        except Exception as e:
            logger.error(f"Error in method_name: {e}")
            raise ThingSpeakError(f"Failed to ...: {e}")
```

### Error Handling

Always use the error utilities:

```python
from utils.errors import (
    error_response,
    success_response,
    ValidationError,
    NotFoundError,
    ThingSpeakError
)

# In route handlers
try:
    # ... code ...
    return success_response(data=result, message="Success message")
except ValidationError as e:
    return error_response(str(e), 400)
except NotFoundError as e:
    return error_response(str(e), 404)
except ThingSpeakError as e:
    return error_response(str(e), 500)
```

### Logging

Use the structured logger:

```python
from utils.logging_config import logger

# Log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include stack trace
```

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_validation.py

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html
```

### Writing Tests

Tests should be comprehensive and follow these patterns:

#### Unit Tests

```python
import unittest
from validators.patient_validator import validate_patient_data
from utils.errors import ValidationError


class TestPatientValidator(unittest.TestCase):
    """Test patient data validation."""
    
    def test_valid_patient_data(self):
        """Test validation with valid patient data."""
        data = {
            "patient_id": "P001",
            "name": "John Doe",
            "floor": "3",
            "room": "301",
            "bed": "A",
            "age": "45",
            "gender": "Male",
            "notes": "Test patient"
        }
        
        result = validate_patient_data(data)
        self.assertEqual(result["patient_id"], "P001")
        self.assertEqual(result["name"], "John Doe")
    
    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "name": "John Doe",
            # Missing patient_id
            "floor": "3",
            "room": "301",
            "bed": "A",
            "age": "45",
            "gender": "Male"
        }
        
        with self.assertRaises(ValidationError) as cm:
            validate_patient_data(data)
        
        self.assertIn("patient_id", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
```

#### Integration Tests

```python
import unittest
from app import app


class TestPatientAPI(unittest.TestCase):
    """Integration tests for patient API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_add_patient_success(self):
        """Test adding a valid patient."""
        patient_data = {
            "patient_id": "P999",
            "name": "Test Patient",
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "30",
            "gender": "Male",
            "notes": "Test"
        }
        
        response = self.client.post(
            '/api/patients',
            json=patient_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
```

### Test Coverage

Aim for high test coverage:

- **Routes**: Test all endpoints (success and error cases)
- **Validators**: Test all validation rules
- **Services**: Test all business logic
- **Utils**: Test utility functions

---

## Documentation

### Code Documentation

- **Docstrings**: Add to all functions, classes, and modules
- **Comments**: Explain complex logic, not obvious code
- **Type hints**: Use where helpful

### API Documentation

When adding or modifying API endpoints:

1. Update `swagger.yaml` with the endpoint definition
2. Include request/response examples
3. Document all parameters and error codes
4. Add to the appropriate tag (Patients, Prescriptions, etc.)

### User Documentation

When adding features visible to users:

1. Update `README.md` with usage instructions
2. Add to appropriate sections (Features, API Endpoints, etc.)
3. Include examples and screenshots if applicable

### Architecture Documentation

When making architectural changes:

1. Update `docs/ARCHITECTURE.md`
2. Update diagrams if component relationships change
3. Document design decisions and trade-offs

---

## Pull Request Process

### Before Creating a PR

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Template

When creating a pull request, include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (please describe)

## Related Issues
Closes #123

## Changes Made
- Added patient search functionality
- Updated validation logic
- Added tests for new feature

## Testing Done
- Ran all existing tests (all pass)
- Added 5 new tests for search functionality
- Manually tested search endpoint with various inputs

## Screenshots (if applicable)
[Add screenshots of UI changes]

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Comments added for complex code
- [x] Documentation updated
- [x] Tests added/updated
- [x] All tests passing
- [x] No new warnings introduced
```

### PR Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged
5. **Cleanup**: Delete your feature branch after merge

### Responding to Feedback

- Be receptive to feedback
- Ask questions if feedback is unclear
- Make requested changes promptly
- Push additional commits to address feedback
- Thank reviewers for their time

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Gather information** (error messages, steps to reproduce, etc.)

### Bug Report Template

```markdown
## Bug Description
Clear and concise description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.9.5]
- Browser (if applicable): [e.g., Chrome 95]

## Error Messages
```
Paste error messages here
```

## Screenshots
[Add screenshots if applicable]

## Additional Context
Any other relevant information
```

### Feature Request Template

```markdown
## Feature Description
Clear and concise description of the feature

## Use Case
Describe the problem this feature would solve

## Proposed Solution
How you think this should work

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information
```

---

## Additional Resources

### Documentation

- **README.md**: Project overview and quick start
- **docs/ARCHITECTURE.md**: System architecture and design
- **docs/DEPLOYMENT.md**: Deployment guide
- **swagger.yaml**: API specification
- **.github/copilot-instructions.md**: AI agent guidelines

### External Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [ThingSpeak API Documentation](https://www.mathworks.com/help/thingspeak/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

### Getting Help

- **GitHub Issues**: For project-specific questions
- **Stack Overflow**: For general Python/Flask questions
- **ThingSpeak Community**: For ThingSpeak-related questions

---

## Recognition

Contributors who make significant contributions will be:
- Listed in the project's contributors section
- Credited in release notes
- Mentioned in relevant documentation

Thank you for contributing to eMAR! Your efforts help improve healthcare technology.

---

*Last Updated: November 15, 2025*
