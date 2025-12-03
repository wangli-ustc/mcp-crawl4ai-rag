# Installation and Deployment

<cite>
**Referenced Files in This Document**   
- [Dockerfile](file://Dockerfile)
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py)
- [supabase/instruction.sh](file://supabase/instruction.sh)
- [pyproject.toml](file://pyproject.toml)
- [README.md](file://README.md)
- [crawled_pages.sql](file://crawled_pages.sql)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Standalone Docker Deployment](#standalone-docker-deployment)
4. [Native Python Execution](#native-python-execution)
5. [Production Considerations](#production-considerations)
6. [Supabase Database Setup](#supabase-database-setup)
7. [Resource Requirements and Performance Tuning](#resource-requirements-and-performance-tuning)
8. [Conclusion](#conclusion)

## Introduction
This document provides comprehensive guidance for installing and deploying the Crawl4AI RAG MCP server using three primary methods: Docker Compose, standalone Docker, and native Python execution. The server enables AI agents to crawl websites, store content in a vector database (Supabase), and perform Retrieval-Augmented Generation (RAG) over the crawled content. The deployment options support various environments, from development to production, with considerations for dependency management, system-level requirements, and performance optimization.

**Section sources**
- [README.md](file://README.md#L1-L773)

## Docker Compose Deployment
Docker Compose provides a convenient way to manage multi-container applications, including the Crawl4AI RAG MCP server and its dependencies. While a dedicated `docker-compose.yml` file is not present in the repository, the `supabase/instruction.sh` script demonstrates the pattern for setting up a Supabase instance using Docker Compose, which can be adapted for the Crawl4AI server.

The following `docker-compose.yml` example configures the Crawl4AI RAG MCP server with environment variable injection, volume mounting, and network configuration:

```yaml
version: '3.8'

services:
  crawl4ai-mcp:
    build: .
    ports:
      - "8051:8051"
    environment:
      - HOST=0.0.0.0
      - PORT=8051
      - TRANSPORT=sse
      - USE_COPILOT_EMBEDDINGS=false
      - USE_COPILOT_CHAT=false
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - MODEL_CHOICE=gpt-4o-mini
      - USE_CONTEXTUAL_EMBEDDINGS=false
      - USE_HYBRID_SEARCH=false
      - USE_AGENTIC_RAG=false
      - USE_RERANKING=false
      - USE_KNOWLEDGE_GRAPH=false
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - CRAWL_STATIC_CONTENT_ONLY=false
      - USE_AGENTIC_RAG=false
    volumes:
      - .:/app
      - playwright-browsers:/app/.cache/ms-playwright
    networks:
      - crawl4ai-network
    depends_on:
      - supabase-db
    restart: unless-stopped

  supabase-db:
    image: supabase/postgres:15.3.0
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${SUPABASE_DB_PASSWORD}
    volumes:
      - supabase-data:/var/lib/postgresql/data
    networks:
      - crawl4ai-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  playwright-browsers:
  supabase-data:

networks:
  crawl4ai-network:
    driver: bridge
```

To deploy with Docker Compose:
1. Create a `.env` file with the required environment variables.
2. Save the `docker-compose.yml` file in the project root.
3. Run `docker compose up -d` to start the services in detached mode.
4. Monitor logs with `docker compose logs -f` to ensure proper initialization.

The configuration includes volume mounting for persistent data storage and browser cache, environment variable injection for configuration, and a custom network for service communication.

**Section sources**
- [Dockerfile](file://Dockerfile#L1-L22)
- [supabase/instruction.sh](file://supabase/instruction.sh#L1-L27)
- [README.md](file://README.md#L87-L102)

## Standalone Docker Deployment
For environments where Docker Compose is not available or desired, the Crawl4AI RAG MCP server can be deployed as a standalone Docker container. The process involves building a Docker image from the provided `Dockerfile` and running it with the necessary environment variables and port mappings.

Build the Docker image:
```bash
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .
```

Run the container:
```bash
docker run --env-file .env -p 8051:8051 --name crawl4ai-mcp -d mcp/crawl4ai-rag
```

The `Dockerfile` specifies a Python 3.12-slim base image, installs dependencies using `uv pip`, and sets up the application with the `crawl4ai-setup` command. The container exposes the configured port (default 8051) and runs the `src/crawl4ai_mcp.py` script as the entry point.

For production deployments, consider the following enhancements:
- Use a dedicated Docker network for service isolation.
- Mount volumes for persistent data and browser cache.
- Configure health checks to monitor container status.
- Set resource limits for CPU and memory.

The standalone Docker approach provides a lightweight and portable deployment option, suitable for both development and production environments.

**Section sources**
- [Dockerfile](file://Dockerfile#L1-L22)
- [README.md](file://README.md#L95-L102)

## Native Python Execution
For environments where Docker is not feasible, the Crawl4AI RAG MCP server can be executed natively using Python. This method requires Python 3.12 or higher and the `uv` package manager for dependency management.

### Dependency Resolution with uv
The recommended approach for native installation uses `uv`, a fast Python package installer and resolver. First, install `uv` if not already available:
```bash
pip install uv
```

Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows
```

Install project dependencies:
```bash
uv pip install -e .
crawl4ai-setup
```

### Handling System-Level Dependencies
The application relies on Playwright for browser automation, which requires system-level dependencies for Chromium. These can be installed with:
```bash
playwright install chromium
```

For environments without sudo access, the `install_deps_without_sudo.py` script provides an alternative installation method that installs Python packages and Playwright browsers without requiring elevated privileges.

### Running Without Sudo
The `install_deps_without_sudo.py` script automates the installation process for restricted environments. It installs Python packages using `uv pip`, installs Playwright browsers, and runs the `crawl4ai-setup` command. System-level dependencies for Playwright are not installed, which may require coordination with system administrators.

To use the script:
```bash
python install_deps_without_sudo.py
```

This approach enables deployment in shared servers, HPC clusters, or other environments with limited permissions, providing a viable alternative to Docker-based deployments.

**Section sources**
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py#L1-L117)
- [pyproject.toml](file://pyproject.toml#L1-L40)
- [README.md](file://README.md#L102-L146)

## Production Considerations
Deploying the Crawl4AI RAG MCP server in production requires attention to process monitoring, logging, and container orchestration to ensure reliability, scalability, and maintainability.

### Process Monitoring
Implement process monitoring to detect and recover from failures. Tools like `supervisord`, `systemd`, or container-native solutions can monitor the application process and restart it if it crashes. For Docker deployments, use the `restart: unless-stopped` policy to ensure automatic recovery from container failures.

### Logging
Configure comprehensive logging to capture application events, errors, and performance metrics. The server generates initialization logs that include configuration summaries and readiness messages. In production, redirect logs to a centralized logging system like ELK Stack, Fluentd, or cloud-based solutions for analysis and monitoring.

### Container Orchestration
For scalable deployments, use container orchestration platforms like Kubernetes, Docker Swarm, or cloud-managed services (e.g., AWS ECS, Google Cloud Run). These platforms provide features for load balancing, auto-scaling, service discovery, and rolling updates, enabling the application to handle varying workloads and ensuring high availability.

Orchestration configurations should include:
- Health checks to verify service readiness.
- Resource limits and requests for CPU and memory.
- Persistent storage for database and cache data.
- Network policies for service communication.
- Secrets management for sensitive configuration.

These practices ensure the application can scale horizontally, recover from failures, and maintain performance under load.

**Section sources**
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L222-L268)
- [README.md](file://README.md#L425-L482)

## Supabase Database Setup
The Crawl4AI RAG MCP server uses Supabase as its vector database for storing crawled content and enabling semantic search. Proper database setup is critical for the application's functionality.

### Database Initialization
Before running the server, initialize the Supabase database with the required tables and extensions. The `crawled_pages.sql` script contains the SQL commands to create the necessary schema:

1. Enable the `pgvector` extension for vector similarity search.
2. Create tables for crawled pages, code examples, and sources.
3. Define indexes for efficient querying.
4. Set up row-level security policies.

To initialize the database:
1. Access the Supabase SQL Editor in the dashboard.
2. Paste the contents of `crawled_pages.sql`.
3. Execute the script to create the schema.

The script creates three main tables:
- `sources`: Stores metadata about crawled sources.
- `crawled_pages`: Stores content chunks with vector embeddings.
- `code_examples`: Stores extracted code examples with summaries.

### Integration with Existing Supabase Projects
To integrate with an existing Supabase project, ensure the database has the `pgvector` extension enabled and the required tables and functions are present. The application connects to Supabase using the `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` environment variables, which can be obtained from the Supabase dashboard.

The `supabase/instruction.sh` script demonstrates how to set up a self-hosted Supabase instance using Docker, which can be adapted for production deployments requiring full control over the database environment.

**Section sources**
- [crawled_pages.sql](file://crawled_pages.sql#L1-L175)
- [supabase/instruction.sh](file://supabase/instruction.sh#L1-L27)
- [README.md](file://README.md#L151-L160)

## Resource Requirements and Performance Tuning
The Crawl4AI RAG MCP server's resource requirements and performance characteristics vary based on deployment scale and configuration options.

### Resource Requirements
- **CPU**: Moderate to high, depending on crawling concurrency and RAG processing.
- **Memory**: Minimum 2GB, recommended 4GB or more for optimal performance.
- **Storage**: Depends on the volume of crawled content; SSD storage recommended for database performance.
- **Network**: Stable internet connection for crawling and API access.

For large-scale deployments, consider the impact of RAG strategies like contextual embeddings, hybrid search, and reranking, which increase computational requirements.

### Performance Tuning
Optimize performance by adjusting configuration parameters:
- **Crawling concurrency**: Reduce `max_concurrent` in `smart_crawl_url` to prevent memory issues.
- **Rate limiting**: Adjust `COPILOT_REQUESTS_PER_MINUTE` to match API limits.
- **Caching**: Enable caching strategies to reduce redundant processing.
- **Indexing**: Optimize database indexes for query patterns.

Monitor application performance and adjust resources based on observed usage patterns. For containerized deployments, set appropriate resource limits and requests to ensure stable operation.

**Section sources**
- [README.md](file://README.md#L447-L482)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L679-L709)

## Conclusion
The Crawl4AI RAG MCP server offers flexible deployment options to accommodate various environments and requirements. Docker Compose provides a convenient solution for multi-container setups, standalone Docker enables portable deployments, and native Python execution supports environments without containerization. Production deployments should incorporate process monitoring, logging, and container orchestration for reliability and scalability. Proper Supabase database setup is essential for functionality, and resource requirements should be tuned based on deployment scale and usage patterns. By following these guidelines, users can successfully deploy and operate the Crawl4AI RAG MCP server for advanced web crawling and RAG capabilities.

**Section sources**
- [README.md](file://README.md#L1-L773)
- [Dockerfile](file://Dockerfile#L1-L22)
- [install_deps_without_sudo.py](file://install_deps_without_sudo.py#L1-L117)