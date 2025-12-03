# Environment Variables

<cite>
**Referenced Files in This Document**   
- [test_mcp_server.py](file://tests/test_mcp_server.py)
- [run_all_tests.py](file://tests/run_all_tests.py)
- [README.md](file://README.md)
- [dashscope_client.py](file://src/dashscope_client.py)
- [iflow_client.py](file://src/iflow_client.py)
- [utils.py](file://src/utils.py)
- [crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)
- [query_rag.py](file://scripts/query_rag.py)
- [test_qwen_integration.py](file://tests/test_qwen_integration.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Environment Variables](#core-environment-variables)
3. [AI Provider Configuration](#ai-provider-configuration)
4. [Conditional Feature Dependencies](#conditional-feature-dependencies)
5. [Development vs Production Configuration](#development-vs-production-configuration)
6. [Security and Access Controls](#security-and-access-controls)
7. [Common Configuration Errors and Troubleshooting](#common-configuration-errors-and-troubleshooting)
8. [Validation and Testing](#validation-and-testing)

## Introduction
This document provides comprehensive guidance on configuring environment variables for the Crawl4AI RAG MCP server. The system relies on various environment variables to control database connections, AI provider integrations, feature toggles, and security settings. Proper configuration is essential for system operation, with special attention required for security-sensitive fields such as API keys and database credentials. This documentation covers all environment variables, their purposes, dependencies, and best practices for secure configuration across different environments.

## Core Environment Variables

The Crawl4AI RAG MCP server requires several core environment variables for database connectivity and basic operation. These variables are essential for the system to function properly and must be configured before deployment.

**SUPABASE_URL** and **SUPABASE_SERVICE_KEY** are required for connecting to the Supabase database, which serves as the vector database for RAG operations. The URL specifies the Supabase project endpoint, while the service key provides administrative access for reading and writing data. These credentials must be properly configured in the `.env` file for both Docker and direct execution scenarios.

**NEO4J_URI**, **NEO4J_USER**, and **NEO4J_PASSWORD** are required when the knowledge graph functionality is enabled via the **USE_KNOWLEDGE_GRAPH** flag. The URI typically follows the format `bolt://localhost:7687` for local installations, while the user is usually `neo4j` by default. The password must be set during Neo4j installation and should be a strong, unique value.

The system includes validation logic in test scripts that checks for the presence of these variables. When **USE_KNOWLEDGE_GRAPH** is enabled, the system verifies that all Neo4j credentials are present and valid. Similarly, Supabase configuration is validated to ensure the database connection can be established before accepting client connections.

**Section sources**
- [test_mcp_server.py](file://tests/test_mcp_server.py#L84-L109)
- [README.md](file://README.md#L234-L242)
- [run_all_tests.py](file://tests/run_all_tests.py#L172-L174)

## AI Provider Configuration

The system supports multiple AI providers for embeddings and chat completions, with configuration options that allow users to select their preferred service. The AI provider configuration is controlled by several environment variables that determine which services are used for different operations.

**EMBEDDING_PROVIDER** options are managed through **USE_QWEN_EMBEDDINGS** and **USE_COPILOT_EMBEDDINGS**. When **USE_QWEN_EMBEDDINGS** is set to `true`, the system uses local Qwen embedding models, which are downloaded and cached locally. This option is recommended for privacy-sensitive applications as it keeps data processing on-premises. When **USE_COPILOT_EMBEDDINGS** is enabled, the system uses GitHub Copilot's embedding API with the `text-embedding-3-small` model.

For chat completions, the system supports **DASHSCOPE_API_KEY** for Alibaba Cloud's Qwen models and **IFLOW_API_KEY** for iFlow services. The **dashscope_client.py** file validates that **DASHSCOPE_API_KEY** is set before making API calls, raising a `ValueError` if the key is missing. Similarly, **iflow_client.py** requires **IFLOW_API_KEY** to be present, with an optional **IFLOW_API_BASE** variable to override the default API endpoint.

The system implements a fallback mechanism for embedding providers, with a preference order of Qwen → Copilot → OpenAI. This is implemented in **utils.py**, where the code checks **USE_QWEN_EMBEDDINGS** first, then falls back to **USE_COPILOT_EMBEDDINGS** if Qwen fails or is disabled, and finally attempts OpenAI if both are unavailable.

**Section sources**
- [utils.py](file://src/utils.py#L135-L156)
- [dashscope_client.py](file://src/dashscope_client.py#L33-L35)
- [iflow_client.py](file://src/iflow_client.py#L130-L132)
- [README.md](file://README.md#L244-L264)

## Conditional Feature Dependencies

Several features in the Crawl4AI RAG MCP server are controlled by environment variables that act as feature flags, enabling or disabling specific functionality based on configuration. These conditional dependencies ensure that resources are only allocated for features that are actively used.

**USE_KNOWLEDGE_GRAPH** is a critical feature flag that enables AI hallucination detection and repository analysis using Neo4j. When this variable is set to `true`, the system requires valid Neo4j credentials (**NEO4J_URI**, **NEO4J_USER**, **NEO4J_PASSWORD**) to be present. The knowledge graph functionality provides three tools: `parse_github_repository` for indexing codebases, `check_ai_script_hallucinations` for validating AI-generated code, and `query_knowledge_graph` for exploring indexed repositories.

**USE_AGENTIC_RAG** enables specialized code example extraction and storage. When enabled, the system identifies code blocks (≥300 characters) during crawling, extracts them with surrounding context, generates summaries, and stores them in a separate vector database table designed for code search. This feature provides the `search_code_examples` tool that AI agents can use to find specific code implementations. The **crawl4ai_mcp.py** file checks this flag before allowing code example searches.

Other conditional features include **USE_HYBRID_SEARCH** (combines vector and keyword search), **USE_RERANKING** (applies cross-encoder reranking to improve result relevance), and **USE_CONTEXTUAL_EMBEDDINGS** (enhances embeddings with document context). These features can be enabled independently and are validated in the test suite to ensure proper configuration.

**Section sources**
- [test_mcp_server.py](file://tests/test_mcp_server.py#L157-L161)
- [crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L1369-L1371)
- [README.md](file://README.md#L352-L359)

## Development vs Production Configuration

The Crawl4AI RAG MCP server supports different configuration profiles for development and production environments, allowing users to optimize settings based on their use case. The system provides recommended configurations for different scenarios, balancing performance, cost, and functionality.

For **development environments**, a minimal configuration is recommended to reduce startup time and resource usage. This includes disabling non-essential features like **USE_RERANKING**, **USE_KNOWLEDGE_GRAPH**, and **USE_CONTEXTUAL_EMBEDDINGS**. The **query_rag.py** script provides verbose output that shows the current configuration, including embedding provider, reranking status, and Agentic RAG status, which is useful for development debugging.

For **production environments**, a more comprehensive configuration is recommended to maximize retrieval quality. The recommended production configuration includes **USE_HYBRID_SEARCH=true**, **USE_RERANKING=true**, and **USE_CONTEXTUAL_EMBEDDINGS=true** for improved search precision. For AI coding assistants, **USE_AGENTIC_RAG=true** is recommended to enable code example extraction.

The system supports both Docker and direct execution, with different configuration approaches. In Docker, environment variables are passed via the `--env-file` flag or individual `-e` flags, while direct execution uses a `.env` file loaded with `python-dotenv`. The **README.md** provides sample configurations for both SSE and Stdio transports, showing how to properly configure environment variables in different deployment scenarios.

**Section sources**
- [README.md](file://README.md#L373-L407)
- [query_rag.py](file://scripts/query_rag.py#L308-L313)
- [test_mcp_server.py](file://tests/test_mcp_server.py#L157-L161)

## Security and Access Controls

Proper security configuration is critical for the Crawl4AI RAG MCP server, particularly for environment variables that contain sensitive credentials. The system implements several security measures to protect sensitive information and prevent unauthorized access.

Security-sensitive fields such as **SUPABASE_SERVICE_KEY**, **NEO4J_PASSWORD**, **OPENAI_API_KEY**, **GITHUB_TOKEN**, **DASHSCOPE_API_KEY**, and **IFLOW_API_KEY** should never be hardcoded in source files or committed to version control. The system uses environment variables to store these credentials, following the twelve-factor app methodology. The test suite (**run_all_tests.py**) masks these values when displaying environment variables, showing asterisks instead of the actual values.

Environment isolation is recommended to prevent credential leakage between environments. Separate `.env` files should be maintained for development, staging, and production, with appropriate access controls. The **SUPABASE_SERVICE_KEY** in particular should have restricted permissions in production, limiting access to only the necessary database tables.

Access controls should be implemented at multiple levels: network-level controls to restrict access to the MCP server, application-level authentication for client connections, and database-level permissions for Supabase and Neo4j. The Neo4j database should be protected with a strong password and, if possible, additional authentication mechanisms like JWT tokens.

**Section sources**
- [run_all_tests.py](file://tests/run_all_tests.py#L161-L164)
- [README.md](file://README.md#L206-L242)
- [dashscope_client.py](file://src/dashscope_client.py#L33-L35)

## Common Configuration Errors and Troubleshooting

Several common configuration errors can prevent the Crawl4AI RAG MCP server from operating correctly. The system includes comprehensive validation and troubleshooting tools to help identify and resolve these issues.

Missing or invalid environment variables are the most common configuration error. The **run_all_tests.py** script performs a comprehensive environment check, identifying missing critical configurations such as Neo4j credentials or AI API keys. When **USE_KNOWLEDGE_GRAPH** is enabled but Neo4j credentials are missing, the system displays a clear error message indicating the configuration gap.

For AI provider configuration, common issues include missing API keys, expired tokens, or rate limiting. The system implements automatic token refresh for GitHub Copilot when 401 authentication errors occur, and exponential backoff for rate limit (429) and server (5xx) errors. The **COPILOT_REQUESTS_PER_MINUTE** variable allows users to configure rate limits based on their subscription tier.

Startup issues are often related to model downloads and loading. The system may take 30 seconds to 2+ minutes to initialize due to downloading and loading models like Qwen3-Embedding-0.6B (~1.2GB) and Qwen3-Reranker-0.6B (~1.2GB). Users can reduce startup time by disabling unused features like **USE_RERANKING** or **USE_KNOWLEDGE_GRAPH**.

The **query_rag.py** script provides a command-line interface for testing the RAG system, allowing users to verify their configuration and troubleshoot issues. It can list available sources, perform searches with filtering, and display verbose configuration information to help diagnose problems.

**Section sources**
- [run_all_tests.py](file://tests/run_all_tests.py#L170-L183)
- [README.md](file://README.md#L447-L479)
- [query_rag.py](file://scripts/query_rag.py#L287-L313)

## Validation and Testing

The Crawl4AI RAG MCP server includes a comprehensive test suite for validating environment variable configuration and system functionality. These tests ensure that all components are properly configured and working together before the server accepts client connections.

The **run_all_tests.py** script serves as the main test runner, executing multiple test suites to validate different aspects of the system. It first checks the environment variables, then runs tests for the MCP server, Neo4j integration, GitHub Copilot integration, and Qwen embedding integration. The test results are summarized at the end, showing which test suites passed or failed.

The **test_mcp_server.py** file contains specific tests for server configuration, including checks for Supabase configuration, Neo4j configuration (when knowledge graph is enabled), and AI provider configuration. It verifies that at least one AI provider (GitHub Copilot or OpenAI) is configured, as this is required for system operation.

Integration tests like **test_qwen_integration.py** verify that specific features work end-to-end. These tests use pytest fixtures to set up test environments with specific configuration options enabled, such as **USE_QWEN_EMBEDDINGS=true** and **USE_COPILOT_EMBEDDINGS=false**, to ensure that the expected embedding provider is used.

The system also includes utility scripts like **check_qwen_dims.py** that help diagnose specific configuration issues, such as mismatched embedding dimensions between the database and search functionality. These tools provide targeted diagnostics for common configuration problems.

**Section sources**
- [run_all_tests.py](file://tests/run_all_tests.py#L185-L233)
- [test_mcp_server.py](file://tests/test_mcp_server.py#L84-L148)
- [test_qwen_integration.py](file://tests/test_qwen_integration.py#L16-L38)
- [check_qwen_dims.py](file://scripts/check_qwen_dims.py#L12-L88)