# Runtime Configuration and Feature Flags

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [src/utils.py](file://src/utils.py)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py)
- [src/copilot_client.py](file://src/copilot_client.py)
- [src/code_summarizer.py](file://src/code_summarizer.py)
- [scripts/crawl_simics_source.py](file://scripts/crawl_simics_source.py)
- [scripts/query_rag.py](file://scripts/query_rag.py)
- [crawled_pages.sql](file://crawled_pages.sql)
- [tests/test_rate_limiting.py](file://tests/test_rate_limiting.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [RAG Strategy Toggles](#rag-strategy-toggles)
3. [Code Summarization Configuration](#code-summarization-configuration)
4. [Simics Source Integration](#simics-source-integration)
5. [Crawling JavaScript Control](#crawling-javascript-control)
6. [Rate Limiting Configuration](#rate-limiting-configuration)
7. [Configuration Profiles](#configuration-profiles)
8. [Feature Flag Interactions](#feature-flag-interactions)
9. [Conclusion](#conclusion)

## Introduction
This document provides comprehensive guidance on runtime configuration and feature flags for the Crawl4AI RAG MCP server. The system offers a flexible configuration framework that enables users to optimize search quality, performance, and functionality based on specific use cases and resource constraints. The configuration is primarily managed through environment variables in a `.env` file, allowing for easy customization without code changes. This document details the key configuration options, their impact on system behavior, and recommended settings for different scenarios.

**Section sources**
- [README.md](file://README.md#L205-L407)

## RAG Strategy Toggles

### USE_CONTEXTUAL_EMBEDDINGS
The `USE_CONTEXTUAL_EMBEDDINGS` flag enables enhanced semantic understanding by generating contextual information for each document chunk. When enabled, the system passes both the full document and specific chunk to an LLM (configured via `MODEL_CHOICE`) to generate enriched context that is embedded alongside the chunk content. This strategy significantly improves retrieval accuracy by preserving document-level context that might otherwise be lost during chunking.

**Impact on Search Quality**: High precision retrieval, especially beneficial for technical documentation where terms have different meanings in different sections.

**Performance Impact**: Slower indexing due to additional LLM calls for each chunk, with associated API costs. The trade-off is improved retrieval accuracy at the expense of indexing speed.

**Section sources**
- [README.md](file://README.md#L322-L328)
- [src/utils.py](file://src/utils.py#L318-L365)

### USE_HYBRID_SEARCH
The `USE_HYBRID_SEARCH` flag combines traditional keyword search with semantic vector search to provide more comprehensive results. The system performs both search types in parallel and intelligently merges results, prioritizing documents that appear in both result sets. This hybrid approach leverages the strengths of both search methodologies.

**Impact on Search Quality**: More robust results, particularly effective for technical content where exact keyword matches are important alongside semantic understanding. Users benefit from finding documents that match both specific terms and conceptual meaning.

**Performance Impact**: Slightly slower search queries due to the need to execute and merge two search types, but no additional API costs—only computational overhead.

**Section sources**
- [README.md](file://README.md#L329-L334)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L302-L362)

### USE_RERANKING
The `USE_RERANKING` flag applies cross-encoder reranking to search results after initial retrieval. It uses a lightweight cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to score each result against the original query, then reorders results by relevance. This post-processing step refines the initial vector search results.

**Impact on Search Quality**: Significantly improved result ordering, especially for complex queries where semantic similarity alone might not capture query intent. Provides better relevance ranking for both regular RAG search and code example search.

**Performance Impact**: Adds approximately 100-200ms to search queries depending on result count, but uses a local model that runs on CPU with no additional API costs.

**Section sources**
- [README.md](file://README.md#L344-L350)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L430-L467)

### USE_AGENTIC_RAG
The `USE_AGENTIC_RAG` flag enables specialized code example extraction and storage. When crawling documentation, the system identifies code blocks (≥300 characters), extracts them with surrounding context, generates summaries, and stores them in a separate vector database table specifically designed for code search. This creates a dedicated repository of code examples accessible through the `search_code_examples` tool.

**Impact on Search Quality**: Essential for AI coding assistants that need to find specific code examples, implementation patterns, or usage examples from documentation. Provides targeted code snippet retrieval capabilities.

**Performance Impact**: Significantly slower crawling due to code extraction and summarization processes, requires more storage space, and incurs additional LLM API calls for summarizing each code example.

**Section sources**
- [README.md](file://README.md#L336-L342)
- [src/utils.py](file://src/utils.py#L589-L717)

## Code Summarization Configuration

### USE_CODE_SUMMARIZATION
The `USE_CODE_SUMMARIZATION` flag controls whether code summarization is enabled when processing source code files. When enabled, the system generates both file-level and chunk-level summaries using domain-specific prompts tailored to Simics source code. This feature is particularly important for the `crawl_simics_source.py` script, which processes DML and Python files from the Simics packages.

**Implementation Details**: The code summarization process follows a multi-step workflow:
1. Generate a file-level summary covering the overall purpose and key components
2. Chunk the source code using AST-aware chunking
3. Generate chunk-level summaries with context from the file summary
4. Create embeddings that incorporate both the code and its summaries

**Performance Impact**: Enabling code summarization increases processing time but significantly improves search quality by providing rich contextual information about code functionality. The summarization uses the iFlow/Qwen3-Coder-Plus model via the `iflow_client`.

**Section sources**
- [scripts/crawl_simics_source.py](file://scripts/crawl_simics_source.py#L247-L251)
- [src/code_summarizer.py](file://src/code_summarizer.py#L27-L253)

## Simics Source Integration

### CRAWL_SIMICS_SOURCE
The `CRAWL_SIMICS_SOURCE` flag enables integration with Simics source code repositories. When enabled, the system can process DML (Device Modeling Language) and Python files from Simics packages, extracting domain-specific metadata and creating specialized embeddings for hardware simulation code.

**Key Features**:
- **DML File Processing**: Extracts device names, templates, interfaces, register groups, and methods from DML files
- **Python File Processing**: Identifies class definitions, function definitions, and Simics-specific imports
- **GitHub Integration**: Converts local file paths to GitHub URLs for source code linking
- **AST-Aware Chunking**: Uses the astchunk library to intelligently chunk source code while preserving syntactic structure

**Configuration**: The `SIMICS_SOURCE_PATH` environment variable specifies the location of the Simics packages directory. The system automatically detects and processes all `.dml` and `.py` files within this directory and its subdirectories.

**Section sources**
- [scripts/crawl_simics_source.py](file://scripts/crawl_simics_source.py#L619-L622)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L253)

## Crawling JavaScript Control

### CRAWL_STATIC_CONTENT_ONLY
The `CRAWL_STATIC_CONTENT_ONLY` setting controls JavaScript execution during crawling operations. When set to `true`, the crawler disables JavaScript to extract only static HTML content, preventing JavaScript redirects and dynamic content loading. This setting is particularly important for websites that use JavaScript to redirect to different content than expected.

**Use Cases**:
- **Static Content Only**: When you want the original page content without JavaScript redirects
- **Faster Crawling**: For simple pages where dynamic content is not needed
- **Predictable Content Size**: For large documentation sites where JavaScript might load excessive content

**Configuration Precedence**: The system follows a specific priority order for JavaScript control:
1. Tool parameter (`disable_javascript=True/False`) - highest priority
2. Script CLI flag (`--static-only`) - overrides environment
3. Environment variable (`CRAWL_STATIC_CONTENT_ONLY=true`) - default setting
4. System default (`false`) - if nothing else is set

**Section sources**
- [README.md](file://README.md#L489-L529)
- [src/crawl4ai_mcp.py](file://src/crawl4ai_mcp.py#L678-L709)

## Rate Limiting Configuration

### DashScope API Rate Limiting
The system includes comprehensive rate limiting and error handling for the DashScope API integration. The configuration is managed through environment variables that control request frequency and error recovery behavior.

**Key Configuration Options**:
- **DASHSCOPE_API_KEY**: Required API key for authentication
- **Rate Limiting**: Configurable via environment variables with smart throttling
- **Error Handling**: Exponential backoff on 429 rate limit and 5xx server errors
- **Token Refresh**: Automatic refresh on 401 authentication errors

**Resilience Features**:
- Zero downtime with seamless token refresh during operation
- Long-running stability for extended usage without failure
- Comprehensive logging for rate limiting actions
- Smart retry logic with rate limiting for failed requests

**Section sources**
- [src/dashscope_client.py](file://src/dashscope_client.py#L10-L86)
- [tests/test_rate_limiting.py](file://tests/test_rate_limiting.py#L21-L168)

### GitHub Copilot Rate Limiting
The GitHub Copilot integration includes enterprise-grade rate limiting with multiple protection mechanisms:

**Rate Limiting Parameters**:
- **COPILOT_REQUESTS_PER_MINUTE**: Configurable requests per minute (default: 60)
- **Burst Protection**: Maximum of 10 requests per 10 seconds
- **Smart Throttling**: Automatically waits when limits are approached

**Error Handling**:
- Exponential backoff on 429 rate limit and 5xx server errors
- Automatic token refresh on 401 authentication errors
- Smart retry with rate limiting for failed requests
- Maximum backoff time of 30 seconds

**Section sources**
- [src/copilot_client.py](file://src/copilot_client.py#L19-L88)
- [tests/test_rate_limiting.py](file://tests/test_rate_limiting.py#L21-L168)

## Configuration Profiles

### Development Profile
For development environments where rapid iteration is prioritized over production stability:

```env
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=false
USE_RERANKING=false
CRAWL_STATIC_CONTENT_ONLY=true
COPILOT_REQUESTS_PER_MINUTE=60
```

**Rationale**: Disables resource-intensive features like contextual embeddings and reranking to speed up development cycles while maintaining basic search functionality.

**Section sources**
- [README.md](file://README.md#L400-L407)

### Testing Profile
For testing environments that require comprehensive feature validation:

```env
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
CRAWL_STATIC_CONTENT_ONLY=false
COPILOT_REQUESTS_PER_MINUTE=60
```

**Rationale**: Enables all advanced RAG strategies to thoroughly test the system's capabilities and ensure all features work correctly together.

**Section sources**
- [README.md](file://README.md#L382-L389)

### Production Profile
For production environments where stability and performance are critical:

```env
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
CRAWL_STATIC_CONTENT_ONLY=true
COPILOT_REQUESTS_PER_MINUTE=45
```

**Rationale**: Balances advanced search capabilities with conservative rate limiting to ensure system stability under production load. Static content crawling prevents unexpected behavior from JavaScript redirects.

**Section sources**
- [README.md](file://README.md#L374-L380)

## Feature Flag Interactions

### Recommended Configuration Combinations
The system supports various configuration combinations depending on the use case:

**General Documentation RAG**:
```env
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=false
USE_RERANKING=true
```

**AI Coding Assistant with Code Examples**:
```env
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
USE_KNOWLEDGE_GRAPH=false
```

**AI Coding Assistant with Hallucination Detection**:
```env
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
USE_KNOWLEDGE_GRAPH=true
```

**Fast, Basic RAG**:
```env
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false
```

### Interaction Guidelines
When configuring multiple feature flags, consider the following interactions:
- **USE_CONTEXTUAL_EMBEDDINGS** and **USE_RERANKING** work synergistically to improve both indexing and retrieval quality
- **USE_HYBRID_SEARCH** complements all other search strategies by adding keyword matching to semantic search
- **USE_AGENTIC_RAG** requires additional storage and processing resources but enables specialized code search capabilities
- **CRAWL_STATIC_CONTENT_ONLY** should be enabled when predictable content extraction is more important than dynamic content

**Section sources**
- [README.md](file://README.md#L373-L407)

## Conclusion
The Crawl4AI RAG MCP server provides a comprehensive and flexible configuration framework that allows users to optimize the system for various use cases and resource constraints. By understanding the impact of each feature flag on search quality and performance, users can create tailored configurations that balance functionality with efficiency. The system's modular design enables incremental enhancement of capabilities, from basic RAG functionality to advanced AI coding assistant features with hallucination detection. Proper configuration of rate limiting and crawling parameters ensures system stability and predictable behavior in production environments.