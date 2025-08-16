# Changelog

All notable changes to the RescueTime MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-17

### Added

- **Complete RescueTime API Integration**: Full coverage of RescueTime APIs including:
  - Analytic Data API with customizable time ranges and filters
  - Daily Summary Feed API for productivity summaries
  - Alerts Feed API for managing productivity alerts
  - Highlights Feed/POST API for viewing and creating highlights
  - FocusTime APIs for managing focus sessions
  - Offline Time POST API for logging offline work
  
- **FastMCP Server Implementation**: 
  - Built on FastMCP framework for robust MCP server functionality
  - Full asynchronous support for high-performance operations
  - 11 comprehensive MCP tools for all RescueTime interactions
  
- **Production-Ready Features**:
  - Comprehensive type safety with Pydantic models
  - Robust error handling with custom exceptions
  - Structured logging with structlog
  - Environment-based configuration
  - Request timeout and retry handling
  
- **Comprehensive Testing Suite**:
  - Unit tests for all client and server functionality
  - Integration tests with real API interactions
  - Performance benchmarks and load testing
  - Mocking support for development and CI
  
- **Development Tooling**:
  - Pre-commit hooks with quality checks
  - Black code formatting
  - isort import sorting
  - Ruff linting
  - MyPy static type checking
  - pytest testing framework
  
- **Documentation**:
  - Complete API documentation
  - Installation and setup instructions
  - Usage examples and development guidelines
  - Contributing guidelines

### Technical Details

- **Python Support**: Python 3.9+
- **Key Dependencies**: FastMCP, httpx, Pydantic, structlog
- **License**: MIT License
- **Architecture**: Async-first design with comprehensive error handling

### Security

- Environment-based API key management
- No hardcoded secrets or credentials
- Comprehensive .gitignore for sensitive files
- Example configuration template

This initial release provides a complete, production-ready MCP server for RescueTime API integration with all major features implemented and thoroughly tested.