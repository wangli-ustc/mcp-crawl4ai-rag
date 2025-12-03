# Testing and Verification

<cite>
**Referenced Files in This Document**   
- [tests/README.md](file://tests/README.md)
- [tests/run_all_tests.py](file://tests/run_all_tests.py)
- [tests/test_neo4j_integration.py](file://tests/test_neo4j_integration.py)
- [tests/test_copilot_integration.py](file://tests/test_copilot_integration.py)
- [tests/test_qwen_embeddings.py](file://tests/test_qwen_embeddings.py)
- [tests/test_mcp_server.py](file://tests/test_mcp_server.py)
- [tests/test_rate_limiting.py](file://tests/test_rate_limiting.py)
- [verify_summarization_integration.py](file://verify_summarization_integration.py)
- [scripts/debug_search.py](file://scripts/debug_search.py)
- [scripts/debug_embeddings.py](file://scripts/debug_embeddings.py)
- [src/utils.py](file://src/utils.py)
</cite>

## Table of Contents
1. [Test Suite Organization](#test-suite-organization)
2. [Running Tests with run_all_tests.py](#running-tests-with-run_all_testspy)
3. [Core Test Cases](#core-test-cases)
4. [Verification Workflows](#verification-workflows)
5. [Debugging Scripts](#debugging-scripts)
6. [Test Data Management and Mocking Strategies](#test-data-management-and-mocking-strategies)
7. [Writing New Tests](#writing-new-tests)

## Test Suite Organization

The test suite is organized in the `tests/` directory and follows a structured approach to validate the core functionality of the crawl4ai-mcp project. The test suite includes integration tests for Neo4j knowledge graph functionality, GitHub Copilot integration, MCP server validation, and specific components like Qwen embeddings and rate limiting.

The test files are categorized as follows:
- **Core Integration Tests**: These include `test_neo4j_integration.py`, `test_copilot_integration.py`, `test_mcp_server.py`, and `run_all_tests.py` which serves as the test runner.
- **Sample Files**: `sample_code_for_validation.py` provides sample Python code for testing hallucination detection.
- **Specialized Tests**: Additional test files cover specific functionalities such as Qwen embeddings (`test_qwen_embeddings.py`, `test_qwen_integration.py`) and rate limiting (`test_rate_limiting.py`).

The test suite is designed to be run both individually and through the test runner, with appropriate pytest markers for integration tests. The tests automatically load environment variables from a `.env` file, ensuring consistent configuration across different execution contexts.

**Section sources**
- [tests/README.md](file://tests/README.md#L1-L212)

## Running Tests with run_all_tests.py

The `run_all_tests.py` script serves as the primary test runner for the project, orchestrating the execution of all integration tests. The script follows a systematic approach to ensure comprehensive test coverage:

1. **Environment Configuration Check**: The script first validates that all required environment variables are properly set, including Neo4j configuration, AI API credentials (GitHub or OpenAI), and other critical settings.

2. **Sequential Test Execution**: The test runner executes test suites in a specific order:
   - MCP Server Validation
   - Neo4j Integration
   - GitHub Copilot Integration
   - Qwen Embedding Integration

3. **Test Execution Methods**: The script employs different execution strategies based on the test type:
   - Direct function calls for Neo4j and Copilot tests
   - pytest execution for Qwen embedding tests
   - Async execution for MCP server tests

4. **Result Aggregation**: After executing all test suites, the script provides a comprehensive summary of results, indicating which test suites passed or failed.

To run all tests, execute the script from the project root:
```bash
.venv/bin/python tests/run_all_tests.py
```

The test runner exits with code 0 on success and 1 on failure, making it suitable for automated testing pipelines. Individual test files can also be run directly and will automatically load the `.env` file for configuration.

**Section sources**
- [tests/run_all_tests.py](file://tests/run_all_tests.py#L1-L233)

## Core Test Cases

The test suite covers several critical components of the system, each with specific test cases designed to validate functionality and integration.

### Copilot Integration Tests

The GitHub Copilot integration tests validate the functionality of the Copilot client for both embedding generation and chat completions. Key test cases include:

- **Embedding Tests**: Verification of single and batch embedding generation using the Copilot client
- **Chat Completion Tests**: Integration with GPT-4o chat model for generating responses
- **Utils Integration**: Testing the unified embedding and chat functions in the utils module
- **Fallback Behavior**: Ensuring OpenAI fallback works when Copilot is unavailable

The tests use pytest's async functionality to handle asynchronous operations and include comprehensive error handling to ensure robustness.

### Neo4j Connectivity Tests

The Neo4j integration tests validate the connection and functionality of the knowledge graph system. Test cases include:

- **Connection Test**: Verifies Neo4j database connectivity using the configured URI, user, and password
- **Module Import Test**: Ensures all knowledge graph modules load correctly
- **Repository Parsing Test**: Validates the DirectNeo4jExtractor functionality
- **Query Operations Test**: Tests database read/write operations and verifies write permissions
- **Sample Code Generation**: Creates test files for hallucination detection

These tests provide comprehensive coverage of the Neo4j integration, ensuring the knowledge graph functionality is working correctly.

### Qwen Embeddings Tests

The Qwen embedding tests validate the integration of the local Qwen embedding model. Test cases include:

- **Model Loading**: Tests that the Qwen model can be loaded successfully
- **Single and Batch Embeddings**: Verification of embedding creation for single texts and batches
- **Embedding Similarity**: Tests that similar texts produce similar embeddings
- **Fallback Behavior**: Ensures the system handles cases where the Qwen model is not available
- **Error Handling**: Validates proper error handling when embedding creation fails

The tests use mocking to simulate various scenarios and ensure the embedding functionality works correctly under different conditions.

### Rate Limiting Tests

The rate limiting tests validate the rate limiting functionality for the GitHub Copilot client. Test cases include:

- **Basic Rate Limiting**: Tests the core rate limiting functionality with a restrictive configuration
- **Error Backoff**: Validates exponential backoff behavior on rate limit errors (429)
- **Burst Protection**: Tests protection against rapid request bursts
- **Real Client Integration**: Tests rate limiting with the actual Copilot client when a token is available

The tests verify that the rate limiter correctly enforces requests per minute and burst limits, and that it implements proper exponential backoff on errors.

**Section sources**
- [tests/test_copilot_integration.py](file://tests/test_copilot_integration.py#L1-L263)
- [tests/test_neo4j_integration.py](file://tests/test_neo4j_integration.py#L1-L269)
- [tests/test_qwen_embeddings.py](file://tests/test_qwen_embeddings.py#L1-L194)
- [tests/test_rate_limiting.py](file://tests/test_rate_limiting.py#L1-L172)

## Verification Workflows

The `verify_summarization_integration.py` script provides a comprehensive verification workflow to confirm that the chunk summarization functionality is properly integrated into the system. The script performs several key checks:

1. **Import Verification**: Confirms that `generate_chunk_summary` is properly imported in `crawl_simics_source.py`
2. **Function Call Verification**: Checks that `generate_chunk_summary` is actually called in the code
3. **Parallel Processing Verification**: Validates that ThreadPoolExecutor is used for parallel processing of chunk summaries
4. **Metadata Updates**: Verifies that both `file_summary` and `chunk_summary` are added to the metadata
5. **Embedding Content Enhancement**: Confirms that file and chunk summaries are prepended to the embedding content
6. **Configuration Verification**: Checks that the necessary environment variables are set in the `.env` file

The script follows a specific code flow:
- Generate file summary using `generate_file_summary`
- Chunk the file using `smart_chunk_source`
- Generate chunk summaries for all chunks in parallel using ThreadPoolExecutor
- Prepend file and chunk summaries to content
- Add summaries to metadata
- Store in Supabase

The verification script provides detailed implementation details and line numbers where key functionality is located, making it easy to understand and debug the summarization integration.

**Section sources**
- [verify_summarization_integration.py](file://verify_summarization_integration.py#L1-L143)

## Debugging Scripts

The project includes several debugging scripts to help diagnose and resolve common issues with the system.

### debug_search.py

The `debug_search.py` script helps diagnose issues with vector search functionality. It performs the following checks:

- **Database State**: Checks the number of records in the crawled_pages table
- **Sample Records**: Retrieves and displays sample records to verify content
- **Embeddings Check**: Verifies that embeddings exist and are not null or zero
- **Search Function Testing**: Tests both direct RPC calls and the search_documents function with a test query

The script provides detailed output about the database state and search functionality, helping to identify why vector search might return zero results.

### debug_embeddings.py

The `debug_embeddings.py` script provides detailed analysis of embeddings in the system. It performs the following checks:

- **Embedding Statistics**: Counts records with null vs non-null embeddings
- **Sample Embeddings**: Examines sample embeddings to verify their structure and content
- **Direct Search Debug**: Tests direct search with specific parameters to debug search functionality
- **Function Check**: Verifies that the match_crawled_pages function exists and is callable

The script helps identify issues with embedding creation and search functionality by providing detailed information about the embeddings in the database.

**Section sources**
- [scripts/debug_search.py](file://scripts/debug_search.py#L1-L95)
- [scripts/debug_embeddings.py](file://scripts/debug_embeddings.py#L1-L107)

## Test Data Management and Mocking Strategies

The test suite employs several strategies for test data management and mocking to ensure reliable and efficient testing.

### Test Data Management

The tests use a combination of real and generated test data:
- **Sample Code**: The `sample_code_for_validation.py` file provides real Python code for testing hallucination detection
- **Generated Data**: Tests generate their own test data as needed, such as test texts for embedding generation
- **Environment Variables**: Configuration is managed through environment variables loaded from the `.env` file

The test data is designed to be self-contained and not rely on external resources whenever possible, making the tests more reliable and faster to execute.

### Mocking Strategies

The tests employ several mocking strategies to isolate components and test specific functionality:

- **Mock Objects**: The Qwen embedding tests use MagicMock to mock the Supabase client and other dependencies
- **Environment Patching**: Tests use pytest's patch functionality to modify environment variables during test execution
- **Function Mocking**: Specific functions are mocked to test error handling and fallback behavior
- **Parameterized Testing**: The Qwen integration tests use pytest's parametrize feature to test various text lengths

The mocking strategies allow the tests to focus on specific functionality without requiring all dependencies to be available, making the tests more robust and easier to maintain.

**Section sources**
- [src/utils.py](file://src/utils.py#L1-L200)
- [tests/test_qwen_integration.py](file://tests/test_qwen_integration.py#L1-L249)