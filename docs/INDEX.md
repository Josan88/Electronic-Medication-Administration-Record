# Documentation Index

Welcome to the eMAR documentation. This index helps you find the right document for your needs.

## Quick Links

| I want to... | Go to |
|--------------|-------|
| Get started quickly | [README.md](../README.md) |
| Understand the system design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Deploy to production | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Use the API | [API_EXAMPLES.md](API_EXAMPLES.md) |
| Fix a problem | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Contribute code | [CONTRIBUTING.md](CONTRIBUTING.md) |
| See what changed | [CHANGELOG.md](../CHANGELOG.md) |

---

## Documentation by Audience

### For Users / Operators

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview, quick start, basic usage |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |

### For Developers

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, component diagrams, data flows |
| [API_EXAMPLES.md](API_EXAMPLES.md) | API usage in curl, Python, JavaScript, PowerShell |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Code standards, PR process, testing guidelines |
| [VALIDATION_IMPLEMENTATION.md](VALIDATION_IMPLEMENTATION.md) | Input validation layer details |
| [TESTING.md](TESTING.md) | Test suite documentation |
| [TESTING_PLAN.md](TESTING_PLAN.md) | Testing strategy and coverage |

### For DevOps / System Administrators

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local, Docker, and production deployment |
| [LOCAL_DATABASE.md](LOCAL_DATABASE.md) | Local DB architecture and ThingSpeak sync |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Diagnostic commands and fixes |

### For Integration Engineers

| Document | Description |
|----------|-------------|
| [NODERED_IMPLEMENTATION.md](NODERED_IMPLEMENTATION.md) | Node-RED flows for HMI/PLC integration |
| [BULK_WRITE_EXAMPLES.md](BULK_WRITE_EXAMPLES.md) | ThingSpeak Bulk Write API examples |
| [API_EXAMPLES.md](API_EXAMPLES.md) | REST API integration examples |

---

## Documentation by Topic

### Getting Started
1. [README.md](../README.md) - Start here for installation and quick start
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed setup instructions
3. [API_EXAMPLES.md](API_EXAMPLES.md) - First API calls

### Architecture & Design
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System overview and diagrams
2. [LOCAL_DATABASE.md](LOCAL_DATABASE.md) - Dual-storage architecture
3. [IMPROVEMENTS.md](IMPROVEMENTS.md) - Implementation history and decisions

### API Reference
1. **Swagger UI** - http://localhost:5000/api/docs (interactive)
2. [swagger.yaml](../docs/swagger.yaml) - OpenAPI 3.0 specification
3. [API_EXAMPLES.md](API_EXAMPLES.md) - Code examples in multiple languages

### Development
1. [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
2. [VALIDATION_IMPLEMENTATION.md](VALIDATION_IMPLEMENTATION.md) - Validation layer
3. [TESTING.md](TESTING.md) - Running and writing tests
4. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Feature implementation details

### Operations
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving
3. [LOCAL_DATABASE.md](LOCAL_DATABASE.md) - Monitoring sync status

### Integration
1. [NODERED_IMPLEMENTATION.md](NODERED_IMPLEMENTATION.md) - HMI/PLC integration
2. [BULK_WRITE_EXAMPLES.md](BULK_WRITE_EXAMPLES.md) - Batch data operations

---

## Document Descriptions

### Core Documentation

| File | Lines | Purpose |
|------|-------|---------|
| [README.md](../README.md) | ~640 | Main project documentation, quick start, features |
| [ARCHITECTURE.md](ARCHITECTURE.md) | ~710 | System design with Mermaid diagrams |
| [DEPLOYMENT.md](DEPLOYMENT.md) | ~1100 | Complete deployment guide |
| [API_EXAMPLES.md](API_EXAMPLES.md) | ~850 | API usage examples |
| [CONTRIBUTING.md](CONTRIBUTING.md) | ~810 | Developer contribution guide |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | ~400 | Consolidated troubleshooting |
| [CHANGELOG.md](../CHANGELOG.md) | ~200 | Version history |

### Technical Documentation

| File | Purpose |
|------|---------|
| [LOCAL_DATABASE.md](LOCAL_DATABASE.md) | Local JSON database and sync architecture |
| [BULK_WRITE_EXAMPLES.md](BULK_WRITE_EXAMPLES.md) | ThingSpeak Bulk Write API usage |
| [VALIDATION_IMPLEMENTATION.md](VALIDATION_IMPLEMENTATION.md) | Input validation system |
| [ENTRY_ID_RETRY.md](ENTRY_ID_RETRY.md) | Entry ID handling and retry logic |
| [NODERED_IMPLEMENTATION.md](NODERED_IMPLEMENTATION.md) | Node-RED flow documentation |

### Project Management

| File | Purpose |
|------|---------|
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Task tracking and implementation summary |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Feature implementation details |
| [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) | Documentation implementation notes |
| [TESTING.md](TESTING.md) | Test documentation |
| [TESTING_PLAN.md](TESTING_PLAN.md) | Testing strategy |

### Other Files

| File | Location | Purpose |
|------|----------|---------|
| [copilot-instructions.md](../.github/copilot-instructions.md) | `.github/` | AI coding agent guidelines |
| [REPORT.md](../nodered/REPORT.md) | `nodered/` | Detailed Node-RED flow report |
| [swagger.yaml](swagger.yaml) | `docs/` | OpenAPI 3.0 specification |

---

## External Resources

### ThingSpeak
- [ThingSpeak Documentation](https://www.mathworks.com/help/thingspeak/)
- [Bulk Write API](https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html)
- [REST API](https://www.mathworks.com/help/thingspeak/rest-api.html)

### Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/)

### Node-RED
- [Node-RED Documentation](https://nodered.org/docs/)
- [node-red-contrib-modbus](https://flows.nodered.org/node/node-red-contrib-modbus)

---

## Documentation Standards

When updating documentation:

1. **Keep it current** - Update docs when code changes
2. **Use examples** - Show, don't just tell
3. **Cross-reference** - Link to related documents
4. **Date updates** - Note "Last Updated" at document end
5. **Follow format** - Use consistent Markdown styling

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed documentation guidelines.

---

*Last Updated: December 2025*
