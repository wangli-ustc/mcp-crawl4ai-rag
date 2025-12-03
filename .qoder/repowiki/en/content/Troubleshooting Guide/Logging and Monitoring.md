# Logging and Monitoring

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [src/utils.py](file://src/utils.py)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)
- [scripts/debug_search.py](file://scripts/debug_search.py)
- [scripts/debug_embeddings.py](file://scripts/debug_embeddings.py)
- [knowledge_graphs/ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py)
- [tests/test_mcp_server.py](file://tests/test_mcp_server.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Log Levels and Structure](#log-levels-and-structure)
3. [Finding Logs by Operation Type](#finding-logs-by-operation-type)
4. [Structured Logging Format](#structured-logging-format)
5. [Key Diagnostic Messages](#key-diagnostic-messages)
6. [Enabling Verbose Output](#enabling-verbose-output)
7. [Using Diagnostic Scripts](#using-diagnostic-scripts)
8. [Monitoring Recommendations](#monitoring-recommendations)
9. [Test Scripts for Validation](#test-scripts-for-validation)

## Introduction
This document provides comprehensive guidance on logging and monitoring for the Crawl4AI RAG MCP server. It covers log locations, formats, diagnostic messages, and tools for debugging and monitoring system operations. The system uses Python's built-in logging module and print statements for operational visibility, with different components producing logs at various levels of detail.

## Log Levels and Structure

The system employs a combination of Python logging and print statements for different components. The primary log levels used are:

- **INFO**: General operational information, initialization messages, and progress updates
- **WARNING**: Non-critical issues that may require attention
- **ERROR**: Critical failures that prevent normal operation
- **DEBUG**: Detailed diagnostic information (requires explicit enabling)

The MCP server startup sequence produces a standardized set of INFO-level messages that confirm successful initialization of components:

```text
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

These messages provide a quick health check of the system configuration and connectivity status.

**Section sources**
- [README.md](file://README.md#L429-L468)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L222-L268)

## Finding Logs by Operation Type

### Crawling Operations
Crawling logs are primarily generated through print statements in the main MCP server and utility functions. Key log locations include:

- **Crawl initiation**: Messages indicating the start of crawling with JavaScript settings
- **Content extraction**: Information about raw content length and chunking
- **Database storage**: Confirmation of document insertion into Supabase

```python
print(f"🚫 Crawling static content only (JavaScript disabled): {url}")
print(f"   📄 Raw content length: {len(result.markdown)} characters")
print(f"   📦 Split into {len(chunks)} chunks (target: ~{chunk_size} chars per chunk)")
```

### Embedding Operations
Embedding logs are generated when creating vector representations of content. These logs show the embedding provider being used and any errors encountered:

```python
print("Using local Qwen model for embeddings...")
print("Using GitHub Copilot for embeddings...")
print("Using OpenAI for embeddings...")
print(f"Error creating Qwen embeddings: {e}")
```

### Database Operations
Database operations are logged with detailed information about queries and results:

```python
print(f"Total records in crawled_pages: {total_count}")
print(f"Records with non-null embeddings: {len(embedding_check.data)}")
print(f"Direct RPC result: {len(direct_result.data)} results")
```

### Query Execution
Query execution logs provide insight into the search process, including hybrid search combination statistics:

```python
print(f"      📊 Hybrid combination: {both_searches_count} both + {vector_only_count} vector + {keyword_only_count} keyword")
print(f"   🔗 Combined results: {len(final_results)} total from {len(source_ids)} sources")
```

**Section sources**
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L688-L757)
- [src/utils.py](file://src/utils.py#L139-L155)
- [scripts/debug_search.py](file://scripts/debug_search.py#L19-L74)

## Structured Logging Format

The system uses a combination of structured print statements and Python logging. For components using the logging module (primarily knowledge graph tools), the format is:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

This produces timestamps with millisecond precision, logger names, log levels, and messages. For example:

```text
2024-01-15 14:30:25 - ai_hallucination_detector - INFO - Starting hallucination detection for: /path/to/script.py
```

For print-based logging (most components), the format is more informal but consistent in using emoji indicators for different message types:

- **✅** Success/confirmation messages
- **❌** Error/failure messages
- **⚠️** Warning messages
- **🔍** Diagnostic/inspection messages
- **🚀** Startup/initialization messages
- **📊** Statistics/summary messages

**Section sources**
- [knowledge_graphs/ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L23-L27)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L222-L268)

## Key Diagnostic Messages to Watch For

### Critical Errors
These messages indicate serious problems that require immediate attention:

```python
print(f"Failed to initialize Neo4j components: {format_neo4j_error(e)}")
logger.error("Please set NEO4J_PASSWORD environment variable or use --neo4j-password")
print(f"Error creating batch embeddings (attempt {retry + 1}/{max_retries}): {e}")
print(f"Failed to insert batch after {max_retries} attempts: {e}")
```

### Warning Indicators
These messages suggest potential issues that may affect performance or functionality:

```python
print("⚠️  astchunk not available ({e}), falling back to markdown chunking")
print("⚠️  Unsupported source type '{source_type}', falling back to markdown chunking")
print(f"Warning: Zero or invalid embedding detected, creating new one...")
```

### Success Indicators
These messages confirm successful operations and can be used to verify system health:

```python
print("✓ Qwen embedding model loaded successfully")
print("✓ CrossEncoder reranker model loaded successfully")
print("✅ Server is ready to accept connections!")
print(f"Created new source: {source_id}")
print(f"Updated source: {source_id}")
```

### Performance Indicators
These messages provide insight into system performance and resource usage:

```python
print(f"Loading Qwen embedding model on {device}...")
print(f"Creating embeddings for {len(texts)} texts using Qwen model...")
print(f"Attempting to insert records individually...")
print(f"Successfully inserted {successful_inserts}/{len(batch_data)} records individually")
```

**Section sources**
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L199-L215)
- [src/utils.py](file://src/utils.py#L169-L176)
- [knowledge_graphs/ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L295)

## Enabling Verbose Output

### MCP Server Verbose Mode
The MCP server does not have a dedicated verbose mode, but detailed output is produced by default during initialization and operations. The startup sequence provides comprehensive information about the configured components.

### Knowledge Graph Tools Verbose Mode
The knowledge graph tools support a verbose mode through the `--verbose` command-line argument:

```bash
python knowledge_graphs/ai_hallucination_detector.py script.py --verbose
```

This enables INFO-level logging for the detector and its components.

### Debugging Neo4j Connections
For Neo4j connection issues, the system provides specific error messages that help diagnose the problem:

```python
def format_neo4j_error(error: Exception) -> str:
    error_str = str(error).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str or "timeout" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "database" in error_str:
        return "Neo4j database error. Check if the database exists and is accessible."
    else:
        return f"Neo4j error: {str(error)}"
```

### Environment Variables for Debugging
Several environment variables affect logging behavior:

- **CRAWL_STATIC_CONTENT_ONLY**: Controls whether JavaScript is disabled during crawling
- **USE_RERANKING**: Enables or disables the reranking model loading
- **USE_KNOWLEDGE_GRAPH**: Controls whether knowledge graph components are initialized

**Section sources**
- [knowledge_graphs/ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L280-L285)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L193-L219)

## Using Diagnostic Scripts

### debug_search.py
This script helps diagnose why vector search might return zero results by checking the database state and testing search functionality:

```python
def check_database_state():
    """Check what's actually in the database."""
    # 1. Check if there are any records in crawled_pages
    # 2. Get a few sample records
    # 3. Check if embeddings exist and are not null/zero
    # 4. Test a simple search
```

Usage:
```bash
python scripts/debug_search.py
```

The script outputs detailed information about the database contents, embedding status, and search functionality, helping identify issues with data ingestion or search configuration.

### debug_embeddings.py
This script provides detailed analysis of embeddings in the database:

```python
def check_embeddings_detailed():
    """Check embeddings in detail."""
    # 1. Check how many records have null vs non-null embeddings
    # 2. Get sample records with embeddings to examine them
    # 3. Try a direct search with specific parameters to debug
    # 4. Check if the function exists and is callable
```

Usage:
```bash
python scripts/debug_embeddings.py
```

The script provides statistics on embedding completeness, samples of actual embedding values, and tests the search functionality with various parameters.

### test_mcp_server.py
This comprehensive test script validates the MCP server configuration and connectivity:

```python
async def test_full_mcp_server():
    """Run complete MCP server validation."""
    # Tests server process, configuration, database, AI providers, RAG features, tools, and rate limiting
```

Usage:
```bash
python tests/test_mcp_server.py
```

The script provides a detailed summary of the server's configuration status, indicating which components are properly configured and which need attention.

**Section sources**
- [scripts/debug_search.py](file://scripts/debug_search.py#L13-L83)
- [scripts/debug_embeddings.py](file://scripts/debug_embeddings.py#L12-L93)
- [tests/test_mcp_server.py](file://tests/test_mcp_server.py#L215-L268)

## Monitoring Recommendations

### Production Metrics Collection
For production use, implement monitoring of the following key metrics:

- **Server startup time**: Track the time from process start to "Server is ready" message
- **Crawling throughput**: Number of pages crawled per minute
- **Embedding generation rate**: Number of embeddings created per minute
- **Search latency**: Time from query receipt to results returned
- **Database connection health**: Supabase and Neo4j connection status
- **Error rates**: Frequency of failed operations by type

### Alerting on Failures
Set up alerts for the following critical conditions:

- **Server not running**: No process detected with the MCP server script
- **Database connectivity loss**: Supabase or Neo4j connections fail
- **Authentication failures**: Repeated 401 errors with AI providers
- **Rate limiting**: Repeated 429 errors from AI providers
- **Zero search results**: Consistent empty results when content exists
- **Failed embeddings**: Repeated zero-vector embeddings

### Auditing Tool Usage
Implement auditing of tool usage through:

- **Log aggregation**: Collect logs from all components in a central system
- **Structured logging**: Parse and index log messages for querying
- **Usage metrics**: Track frequency of tool calls by type
- **Performance monitoring**: Measure response times for each tool
- **Error tracking**: Monitor error rates by tool and operation type

### Recommended Monitoring Stack
For production deployments, consider implementing:

1. **Centralized logging**: Use ELK stack (Elasticsearch, Logstash, Kibana) or similar
2. **Metrics collection**: Prometheus with Grafana for visualization
3. **Alerting**: Alertmanager or similar for notifications
4. **Distributed tracing**: Jaeger or OpenTelemetry for request tracing
5. **Health checks**: Regular automated validation of system components

**Section sources**
- [README.md](file://README.md#L297-L316)
- [tests/test_mcp_server.py](file://tests/test_mcp_server.py#L215-L268)

## Test Scripts for Validation

### Expected Log Output During Validation
When validating the system with test scripts, expect the following log patterns:

#### Successful Server Startup
```text
============================================================
🚀 MCP Crawl4AI RAG Server Initialization Complete!
============================================================
📊 Embedding Provider: [provider]
🔗 Embedding Model: [model]
💬 Chat Model Provider: [provider]
🤖 Model Choice: [model]
🔍 Reranking Model: [model]
🧠 Knowledge Graph: [Enabled/Disabled]
🗄️  Supabase: Connected
✅ Server is ready to accept connections!
============================================================
```

#### Successful Test Execution
```text
🚀 MCP Server Validation Test
...
📊 VALIDATION SUMMARY
...
🎉 ALL TESTS PASSED! MCP Server is properly configured and running.
```

#### Partial Success
```text
⚠️  Most tests passed. Minor configuration issues detected.
```

#### Failure
```text
❌ Multiple tests failed. Please check configuration.
```

### test_mcp_server.py Output
The test script provides detailed output for each validation category:

```text
🔍 Checking MCP server process...
✅ MCP Server process is running

📋 Testing Server Configuration...
• Transport: sse
• Host: 0.0.0.0
• Port: 8051
✅ Valid transport configuration

🗄️  Testing Database Configuration...
• Supabase: ✅ Configured
• Neo4j: ⚠️  Knowledge graph disabled
```

This structured output makes it easy to identify which components are properly configured and which need attention.

**Section sources**
- [tests/test_mcp_server.py](file://tests/test_mcp_server.py#L217-L267)
- [README.md](file://README.md#L719-L771)