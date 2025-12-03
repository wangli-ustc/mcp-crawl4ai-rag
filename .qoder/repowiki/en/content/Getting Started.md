# Getting Started

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [pyproject.toml](file://pyproject.toml)
- [Dockerfile](file://Dockerfile)
- [mcp.json](file://mcp.json)
- [crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py)
- [crawled_pages.sql](file://crawled_pages.sql)
</cite>

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Starting the MCP Server](#starting-the-mcp-server)
5. [Quick Start Scenarios](#quick-start-scenarios)
6. [Testing and Verification](#testing-and-verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up the Crawl4AI RAG MCP server, ensure you have the following prerequisites installed and configured:

- **Python 3.12+**: Required for running the server directly with uv. The project requires Python 3.12 or higher as specified in the pyproject.toml file.
- **Docker/Docker Desktop**: Recommended for containerized deployment, allowing for consistent environment setup across different systems.
- **Supabase**: Database service for storing crawled content and vector embeddings. You'll need a Supabase project with service key access.
- **Embedding Provider**: Choose one of the following:
  - **OpenAI API key**: For using OpenAI's text-embedding-3-small model
  - **GitHub Copilot subscription and token**: For using GitHub Copilot embeddings
- **Neo4j** (optional): Required only if you plan to use knowledge graph features for AI hallucination detection and repository analysis.

**Section sources**
- [README.md](file://README.md#L75-L83)
- [pyproject.toml](file://pyproject.toml#L10)

## Environment Setup

### Using Docker (Recommended)

Docker provides a consistent environment for running the MCP server. Follow these steps to set up using Docker:

1. **Clone the repository:**
```bash
git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
cd mcp-crawl4ai-rag
```

2. **Build the Docker image:**
```bash
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .
```

The Dockerfile specifies a Python 3.12-slim base image and installs dependencies using uv, a fast Python package installer and resolver.

**Section sources**
- [README.md](file://README.md#L89-L97)
- [Dockerfile](file://Dockerfile)

### Using uv Directly (No Docker)

For direct Python execution, use uv (a fast Python package installer and resolver):

1. **Clone the repository:**
```bash
git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
cd mcp-crawl4ai-rag
```

2. **Install uv if not already installed:**
```bash
pip install uv
```

3. **Create and activate a virtual environment:**
```bash
uv venv
.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate
```

4. **Install dependencies:**
For systems with sudo permissions:
```bash
uv pip install -e .
# To avoid downloading large NVIDIA CUDA packages:
# uv pip install --torch-backend cpu -e .
crawl4ai-setup
```

For systems without sudo permissions (e.g., shared servers, HPC clusters):
```bash
.venv/bin/python install_deps_without_sudo.py
```

The installation script handles Python dependencies, Playwright browsers, and crawl4ai setup without requiring system-level permissions.

**Section sources**
- [README.md](file://README.md#L104-L148)
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py)

## Configuration

### Database Setup

Before running the server, set up the Supabase database with the pgvector extension:

1. Go to the SQL Editor in your Supabase dashboard
2. Create a new query and paste the contents of `crawled_pages.sql`
3. Run the query to create the necessary tables and functions

The SQL script creates three main tables:
- `sources`: Stores information about crawled sources
- `crawled_pages`: Stores documentation chunks with vector embeddings
- `code_examples`: Stores code examples with summaries (when USE_AGENTIC_RAG is enabled)

It also creates similarity search functions and appropriate indexes for efficient querying.

**Section sources**
- [README.md](file://README.md#L151-L159)
- [crawled_pages.sql](file://crawled_pages.sql)

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# MCP Server Configuration
HOST=0.0.0.0
PORT=8051
TRANSPORT=sse

# AI Provider Configuration
USE_COPILOT_EMBEDDINGS=false
USE_COPILOT_CHAT=false

# OpenAI API Configuration (when USE_COPILOT_EMBEDDINGS=false or USE_COPILOT_CHAT=false)
OPENAI_API_KEY=your_openai_api_key

# GitHub Copilot Configuration (when USE_COPILOT_EMBEDDINGS=true or USE_COPILOT_CHAT=true)
GITHUB_TOKEN=your_github_token

# LLM for summaries and contextual embeddings
MODEL_CHOICE=gpt-4o

# RAG Strategies (set to "true" or "false", default to "false")
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Neo4j Configuration (required for knowledge graph functionality)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

**Section sources**
- [README.md](file://README.md#L206-L242)

## Starting the MCP Server

### Using Docker

Start the server with Docker using the environment file:

```bash
docker run --env-file .env -p 8051:8051 mcp/crawl4ai-rag
```

### Using Python

Start the server directly with Python:

```bash
uv run src/crawl4ai_mcp.py
```

### Important: Wait for Server Ready Message

The MCP server takes time to initialize all components before it's ready to accept connections. You must wait for the startup completion message:

```
============================================================
🚀 MCP Crawl4AI RAG Server Initialization Complete!
============================================================

📊 Embedding Provider: Qwen (Local)
🔗 Embedding Model: Qwen/Qwen3-Embedding-0.6B
💬 Chat Model Provider: GitHub Copilot
🤖 Model Choice: gpt-4o-mini
🔍 Reranking Model: Qwen/Qwen3-Reranker-0.6B
🧠 Knowledge Graph: Enabled
🗄️  Supabase: Connected

✅ Server is ready to accept connections!
💡 Connect your MCP client to start using RAG and web crawling tools.
============================================================
```

Initialization time can range from 30 seconds to over 2 minutes depending on your configuration, as the server downloads and loads models, establishes database connections, and verifies external services.

**Section sources**
- [README.md](file://README.md#L410-L482)
- [crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L222-L268)

## Quick Start Scenarios

### Basic RAG Functionality

For a basic RAG setup without knowledge graph features, use this configuration in your `.env` file:

```env
USE_KNOWLEDGE_GRAPH=false
USE_AGENTIC_RAG=false
USE_HYBRID_SEARCH=true
USE_RERANKING=false
USE_CONTEXTUAL_EMBEDDINGS=false
```

Start the server and test with a simple curl request:

```bash
# Start the server
uv run src/crawl4ai_mcp.py

# In another terminal, test the server
curl http://localhost:8051/health
```

Crawl a webpage and perform a RAG query:

```python
# Example Python client code
import requests

# Crawl a single page
requests.post('http://localhost:8051/crawl_single_page', json={
    'url': 'https://example.com/docs'
})

# Perform a RAG query
response = requests.post('http://localhost:8051/perform_rag_query', json={
    'query': 'What is the main feature described in the documentation?'
})
print(response.json())
```

### Full Knowledge Graph Integration

For full knowledge graph integration with AI hallucination detection, use this configuration:

```env
USE_KNOWLEDGE_GRAPH=true
USE_AGENTIC_RAG=true
USE_HYBRID_SEARCH=true
USE_RERANKING=true
USE_CONTEXTUAL_EMBEDDINGS=true
```

First, set up Neo4j:

```bash
# Clone the Local AI Package (recommended)
git clone https://github.com/coleam00/local-ai-packaged.git
cd local-ai-packaged
# Follow instructions to start Neo4j with Docker Compose
```

Then start the MCP server:

```bash
uv run src/crawl4ai_mcp.py
```

Use the knowledge graph tools:

```python
# Parse a GitHub repository into the knowledge graph
requests.post('http://localhost:8051/parse_github_repository', json={
    'repo_url': 'https://github.com/pydantic/pydantic-ai.git'
})

# Check for AI hallucinations in a Python script
requests.post('http://localhost:8051/check_ai_script_hallucinations', json={
    'script_path': '/path/to/your/script.py'
})

# Query the knowledge graph
requests.post('http://localhost:8051/query_knowledge_graph', json={
    'command': 'repos'
})
```

**Section sources**
- [README.md](file://README.md#L373-L398)
- [crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)

## Testing and Verification

After setting up the server, verify your RAG system is working correctly using the included query script:

```bash
# Basic search to test your setup
python scripts/query_rag.py "your search query here"

# List all available sources in your database
python scripts/query_rag.py --list-sources

# Search with specific filtering
python scripts/query_rag.py "device implementation" --source-type python --count 5 --verbose

# Test code examples (requires USE_AGENTIC_RAG=true)
python scripts/query_rag.py "implementation example" --type both
```

Expected results:
- Similarity scores between 0.3-0.8+ (higher = better match)
- Rich metadata showing file paths, methods, classes
- Relevant content matching your search terms
- Multiple sources if you've crawled different sites/codebases

**Section sources**
- [README.md](file://README.md#L715-L771)

## Troubleshooting

### Common Issues

**Memory errors during crawling**: Reduce the `max_concurrent` parameter in `smart_crawl_url` (try 5 instead of 10).

**Rate limiting errors**: Check your API rate limits and adjust `COPILOT_REQUESTS_PER_MINUTE` in `.env`.

**Neo4j connection errors**: Ensure Neo4j is running and the connection details in `.env` are correct. Common issues include:
- Authentication failed: Check NEO4J_USER and NEO4J_PASSWORD
- Cannot connect: Check NEO4J_URI and ensure Neo4j is running
- Database error: Check if the database exists and is accessible

**Supabase connection errors**: Verify your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct.

### Installation Issues on Machines Without Sudo

If working on a restricted environment:

1. Use the provided installation script:
```bash
.venv/bin/python install_deps_without_sudo.py
```

2. If you encounter browser-related errors:
- Ask your system administrator to install Playwright dependencies:
```bash
sudo .venv/bin/python -m playwright install-deps chromium
```
- Or use Docker instead (recommended for restricted environments)

3. Alternative: Use Docker, which has its own isolated environment and doesn't require sudo on the host machine.

**Section sources**
- [README.md](file://README.md#L673-L711)
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py)