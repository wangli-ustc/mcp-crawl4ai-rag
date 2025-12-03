# Installation Issues

<cite>
**Referenced Files in This Document**   
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py)
- [pyproject.toml](file://pyproject.toml)
- [uv.lock](file://uv.lock)
- [README.md](file://README.md)
</cite>

## Table of Contents
1. [Common Installation Problems](#common-installation-problems)
2. [Platform-Specific Issues](#platform-specific-issues)
3. [Dependency Verification](#dependency-verification)
4. [Error Log Interpretation](#error-log-interpretation)
5. [Environment Validation](#environment-validation)

## Common Installation Problems

### Missing Dependencies
Missing dependencies are a common issue during installation. The project requires specific versions of packages as defined in `pyproject.toml` and `uv.lock`. When dependencies are missing, you may encounter import errors or module not found exceptions. To resolve this, ensure you install all dependencies using the correct method:

- **With sudo permissions**: Use `uv pip install -e .` to install all dependencies from `pyproject.toml`
- **Without sudo permissions**: Use the provided script `python install_deps_without_sudo.py` which handles dependency installation without requiring system-level permissions

The `install_deps_without_sudo.py` script installs the following core dependencies:
- crawl4ai==0.6.2
- mcp==1.7.1
- supabase==2.15.1
- openai==1.71.0
- neo4j>=5.28.1
- sentence-transformers>=4.1.0

**Section sources**
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py#L11-L23)
- [pyproject.toml](file://pyproject.toml#L11-L25)

### Python Environment Conflicts
Python environment conflicts can occur when multiple Python versions or virtual environments interfere with each other. The project requires Python 3.12+ as specified in both `pyproject.toml` and `uv.lock`. To avoid conflicts:

1. Create an isolated virtual environment using `uv venv`
2. Activate the environment before installation
3. Ensure your PATH points to the correct Python interpreter

Environment conflicts often manifest as version incompatibility errors or missing module errors even after installation. The `uv.lock` file ensures deterministic builds by pinning dependency versions, preventing conflicts from version mismatches.

**Section sources**
- [pyproject.toml](file://pyproject.toml#L10)
- [uv.lock](file://uv.lock#L3)

### Docker Build Failures
Docker build failures can occur due to several reasons:
- Missing build arguments (PORT)
- Network issues during dependency installation
- Incompatible base images

To build the Docker image successfully:
```bash
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .
```

Common Docker issues include:
- **Build context problems**: Ensure you're running the command from the project root
- **Layer caching issues**: Use `--no-cache` flag if encountering persistent build failures
- **Port conflicts**: Verify the specified port is available on your system

**Section sources**
- [README.md](file://README.md#L95-L98)

### Permission Errors Without Sudo
Permission errors occur when installing system-level dependencies without administrative privileges. The `install_deps_without_sudo.py` script addresses this by:

1. Installing Python packages using `uv pip` without sudo
2. Installing Playwright browsers (chromium) without system dependencies
3. Running crawl4ai setup with user-level permissions

However, Playwright may still require system dependencies that need sudo access. If you encounter browser-related errors:
```bash
sudo {sys.executable} -m playwright install-deps chromium
```

The script provides a warning about this limitation and suggests requesting your system administrator to install the dependencies.

**Section sources**
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py#L47-L57)
- [README.md](file://README.md#L677-L700)

## Platform-Specific Issues

### Linux
On Linux systems, common issues include:
- Missing system libraries for Playwright
- Permission issues with Docker
- Python version conflicts

Solutions:
- Install system dependencies: `sudo apt-get install libgobject-2.0-0`
- Use user namespaces for Docker if permission issues occur
- Use `pyenv` to manage Python versions

### Windows
Windows-specific issues:
- Path length limitations
- PowerShell execution policies
- Antivirus interference with browser binaries

Solutions:
- Enable long paths in Windows settings
- Run PowerShell as administrator with unrestricted execution policy
- Add project directory to antivirus exclusion list

### macOS
macOS issues:
- Gatekeeper blocking downloaded binaries
- Homebrew Python conflicts
- Architecture-specific packages (Apple Silicon vs Intel)

Solutions:
- Allow apps from App Store and identified developers
- Use native Apple Silicon packages when available
- Ensure Xcode command line tools are installed

**Section sources**
- [README.md](file://README.md#L76-L83)

## Dependency Verification

### Crawl4AI Installation
Verify Crawl4AI is correctly installed by checking:
1. The package is listed in your environment: `uv pip list | grep crawl4ai`
2. The setup completed successfully: Look for "crawl4ai setup completed" in installation logs
3. Required dependencies are present: playwright, aiohttp, beautifulsoup4

Test the installation:
```python
from crawl4ai import WebCrawler
crawler = WebCrawler()
```

### Supabase Client
Verify Supabase client installation by:
1. Checking the package version: `uv pip show supabase`
2. Testing the import: `from supabase import create_client`
3. Validating environment variables are set: SUPABASE_URL, SUPABASE_SERVICE_KEY

### Neo4j Drivers
Verify Neo4j driver installation by:
1. Checking the package: `uv pip show neo4j`
2. Testing the connection:
```python
from neo4j import GraphDatabase
driver = GraphDatabase.driver(uri, auth=(user, password))
```

The `test_neo4j_integration.py` script provides comprehensive tests for Neo4j functionality including connection testing, knowledge graph tools, and query operations.

**Section sources**
- [test_neo4j_integration.py](file://tests/test_neo4j_integration.py#L35-L72)
- [pyproject.toml](file://pyproject.toml#L18)

## Error Log Interpretation

### Common Error Patterns
Interpret error logs by identifying patterns:

**Missing Library Errors**:
```
Error: libgobject-2.0.so.0: cannot open shared object file
```
Solution: Install system dependencies with sudo or use Docker.

**Permission Denied**:
```
PermissionError: [Errno 13] Permission denied
```
Solution: Run with appropriate permissions or use user-level installation script.

**Module Not Found**:
```
ModuleNotFoundError: No module named 'crawl4ai'
```
Solution: Verify installation completed successfully and environment is activated.

### Log Analysis Strategy
1. **Identify the error type**: Determine if it's a dependency, permission, or configuration issue
2. **Check the stack trace**: Look for the originating module and line number
3. **Verify prerequisites**: Ensure Python version, system libraries, and environment variables are correct
4. **Consult the installation script**: Compare your process with `install_deps_without_sudo.py`

The installation script provides detailed logging of each step, making it easier to identify where failures occur.

**Section sources**
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py#L27-L36)
- [README.md](file://README.md#L708-L711)

## Environment Validation

### Test Scripts
Validate your environment using the provided test scripts:

**Run all tests**:
```bash
python tests/run_all_tests.py
```

This script checks:
- Neo4j integration
- GitHub Copilot integration
- Qwen embedding integration
- MCP server functionality

**Test specific components**:
```bash
# Test Neo4j integration
python tests/test_neo4j_integration.py

# Test RAG functionality
python scripts/query_rag.py "test query"
```

### Configuration Verification
Verify your `.env` file contains all required variables:
- HOST, PORT, TRANSPORT
- AI provider credentials (OPENAI_API_KEY or GITHUB_TOKEN)
- Database connections (SUPABASE_URL, SUPABASE_SERVICE_KEY)
- Neo4j credentials (if using knowledge graph)

Use the `query_rag.py` script to test your RAG system:
```bash
python scripts/query_rag.py "your search query" --list-sources
```

Expected successful output includes:
- Similarity scores between 0.3-0.8+
- Rich metadata with file paths and context
- Relevant content matching your search terms

**Section sources**
- [run_all_tests.py](file://tests/run_all_tests.py#L186-L232)
- [query_rag.py](file://scripts/query_rag.py#L272-L347)