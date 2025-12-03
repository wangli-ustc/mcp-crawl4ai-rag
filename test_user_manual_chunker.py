"""
Unit tests for UserManualChunker orchestrator.

Tests the end-to-end processing pipeline that coordinates
parsing, chunking, metadata extraction, summarization, and embedding.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from user_manual_chunker import (
    UserManualChunker,
    ProcessingStatistics,
    ChunkerConfig,
    ProcessedChunk,
)


class TestProcessingStatistics(unittest.TestCase):
    """Test cases for ProcessingStatistics."""
    
    def test_initialization(self):
        """Test statistics initialization."""
        stats = ProcessingStatistics()
        
        self.assertEqual(stats.documents_processed, 0)
        self.assertEqual(stats.chunks_created, 0)
        self.assertEqual(stats.total_characters, 0)
        self.assertEqual(stats.summaries_generated, 0)
        self.assertEqual(stats.embeddings_generated, 0)
        self.assertEqual(len(stats.errors), 0)
    
    def test_to_dict(self):
        """Test statistics dictionary conversion."""
        stats = ProcessingStatistics()
        stats.documents_processed = 5
        stats.chunks_created = 20
        stats.total_characters = 10000
        stats.code_chunks = 8
        
        stats_dict = stats.to_dict()
        
        self.assertEqual(stats_dict['documents_processed'], 5)
        self.assertEqual(stats_dict['chunks_created'], 20)
        self.assertEqual(stats_dict['total_characters'], 10000)
        self.assertEqual(stats_dict['code_chunks'], 8)
        self.assertEqual(stats_dict['average_chunk_size'], 500.0)
    
    def test_average_chunk_size_zero_chunks(self):
        """Test average chunk size with zero chunks."""
        stats = ProcessingStatistics()
        stats_dict = stats.to_dict()
        
        self.assertEqual(stats_dict['average_chunk_size'], 0)
    
    def test_error_limit(self):
        """Test error list is limited to 10."""
        stats = ProcessingStatistics()
        for i in range(15):
            stats.errors.append(f"Error {i}")
        
        stats_dict = stats.to_dict()
        
        self.assertEqual(len(stats_dict['errors']), 10)
        self.assertEqual(stats_dict['error_count'], 15)


class TestUserManualChunker(unittest.TestCase):
    """Test cases for UserManualChunker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ChunkerConfig(
            max_chunk_size=500,
            min_chunk_size=100,
            chunk_overlap=50,
            generate_summaries=False,
            generate_embeddings=False
        )
        self.chunker = UserManualChunker(config=self.config)
    
    def test_initialization_default_config(self):
        """Test initialization with default configuration."""
        chunker = UserManualChunker()
        
        self.assertIsNotNone(chunker.config)
        self.assertIsNotNone(chunker.chunker)
        self.assertIsNotNone(chunker.metadata_extractor)
        self.assertIsNotNone(chunker.markdown_parser)
        self.assertIsNotNone(chunker.html_parser)
    
    def test_initialization_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = ChunkerConfig(
            max_chunk_size=1000,
            generate_summaries=True,
            generate_embeddings=True
        )
        chunker = UserManualChunker(config=config)
        
        self.assertEqual(chunker.config.max_chunk_size, 1000)
        self.assertIsNotNone(chunker.summary_generator)
        self.assertIsNotNone(chunker.embedding_generator)
    
    def test_initialization_summaries_disabled(self):
        """Test that summary generator is None when disabled."""
        config = ChunkerConfig(generate_summaries=False)
        chunker = UserManualChunker(config=config)
        
        self.assertIsNone(chunker.summary_generator)
    
    def test_initialization_embeddings_disabled(self):
        """Test that embedding generator is None when disabled."""
        config = ChunkerConfig(generate_embeddings=False)
        chunker = UserManualChunker(config=config)
        
        self.assertIsNone(chunker.embedding_generator)
    
    def test_process_document_markdown(self):
        """Test processing a simple markdown document."""
        markdown_content = """# Introduction

This is a test document for chunking.

## Features

Here are some features:

```python
def hello():
    print("Hello, World!")
```

The function above prints a greeting.
"""
        
        chunks = self.chunker.process_document(
            content=markdown_content,
            source_path="test.md",
            doc_format="markdown"
        )
        
        self.assertGreater(len(chunks), 0)
        self.assertIsInstance(chunks[0], ProcessedChunk)
        self.assertIsNotNone(chunks[0].chunk_id)
        self.assertIsNotNone(chunks[0].content)
        self.assertIsNotNone(chunks[0].metadata)
    
    def test_process_document_html(self):
        """Test processing a simple HTML document."""
        html_content = """
<html>
<body>
<h1>Introduction</h1>
<p>This is a test document.</p>
<h2>Features</h2>
<pre><code>print("Hello")</code></pre>
</body>
</html>
"""
        
        try:
            chunks = self.chunker.process_document(
                content=html_content,
                source_path="test.html",
                doc_format="html"
            )
            
            self.assertGreater(len(chunks), 0)
            self.assertIsInstance(chunks[0], ProcessedChunk)
        except ValueError as e:
            if "lxml" in str(e):
                self.skipTest("lxml not installed - HTML parsing skipped")
            else:
                raise
    
    def test_process_document_invalid_format(self):
        """Test error handling for invalid document format."""
        with self.assertRaises(ValueError) as context:
            self.chunker.process_document(
                content="test",
                source_path="test.txt",
                doc_format="invalid"
            )
        
        self.assertIn("Invalid document format", str(context.exception))
    
    def test_chunk_id_generation(self):
        """Test that chunk IDs are unique."""
        markdown_content = """# Section 1

Content for section 1.

## Section 2

Content for section 2.

### Section 3

Content for section 3.
"""
        
        chunks = self.chunker.process_document(
            content=markdown_content,
            source_path="test.md",
            doc_format="markdown"
        )
        
        # Check uniqueness
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))
        
        # Check format (filename_index_hash)
        for chunk_id in chunk_ids:
            parts = chunk_id.split('_')
            self.assertEqual(len(parts), 3)
            self.assertEqual(parts[0], "test")  # filename
    
    def test_chunk_id_deterministic(self):
        """Test that same content produces same chunk ID."""
        content = "Test content"
        
        chunk_id_1 = self.chunker._generate_chunk_id("test.md", 0, content)
        chunk_id_2 = self.chunker._generate_chunk_id("test.md", 0, content)
        
        self.assertEqual(chunk_id_1, chunk_id_2)
    
    def test_chunk_id_different_content(self):
        """Test that different content produces different chunk IDs."""
        chunk_id_1 = self.chunker._generate_chunk_id("test.md", 0, "Content 1")
        chunk_id_2 = self.chunker._generate_chunk_id("test.md", 0, "Content 2")
        
        self.assertNotEqual(chunk_id_1, chunk_id_2)
    
    def test_statistics_tracking(self):
        """Test that statistics are tracked correctly."""
        markdown_content = """# Introduction

This is a test document.

```python
code = "test"
```
"""
        
        self.chunker.reset_statistics()
        chunks = self.chunker.process_document(
            content=markdown_content,
            source_path="test.md",
            doc_format="markdown"
        )
        
        stats = self.chunker.get_statistics()
        
        self.assertEqual(stats['documents_processed'], 1)
        self.assertEqual(stats['chunks_created'], len(chunks))
        self.assertGreater(stats['total_characters'], 0)
    
    def test_reset_statistics(self):
        """Test statistics reset."""
        # Process document
        self.chunker.process_document(
            content="# Test\n\nContent",
            source_path="test.md",
            doc_format="markdown"
        )
        
        # Reset
        self.chunker.reset_statistics()
        stats = self.chunker.get_statistics()
        
        self.assertEqual(stats['documents_processed'], 0)
        self.assertEqual(stats['chunks_created'], 0)
    
    @patch('user_manual_chunker.user_manual_chunker.SummaryGenerator')
    def test_summaries_generation(self, mock_summary_gen_class):
        """Test that summaries are generated when enabled."""
        # Configure with summaries enabled
        config = ChunkerConfig(
            generate_summaries=True,
            generate_embeddings=False
        )
        
        # Mock summary generator
        mock_gen = MagicMock()
        mock_gen.generate_summary.return_value = "Test summary"
        mock_summary_gen_class.return_value = mock_gen
        
        chunker = UserManualChunker(config=config)
        
        chunks = chunker.process_document(
            content="# Test\n\nContent here.",
            source_path="test.md",
            doc_format="markdown"
        )
        
        # Verify summaries were generated
        for chunk in chunks:
            self.assertEqual(chunk.summary, "Test summary")
        
        self.assertGreater(mock_gen.generate_summary.call_count, 0)
    
    @patch('user_manual_chunker.user_manual_chunker.EmbeddingGenerator')
    def test_embeddings_generation(self, mock_embedding_gen_class):
        """Test that embeddings are generated when enabled."""
        # Configure with embeddings enabled
        config = ChunkerConfig(
            generate_summaries=False,
            generate_embeddings=True
        )
        
        # Mock embedding generator
        mock_gen = MagicMock()
        mock_embedding_gen_class.return_value = mock_gen
        
        chunker = UserManualChunker(config=config)
        
        chunks = chunker.process_document(
            content="# Test\n\nContent here.",
            source_path="test.md",
            doc_format="markdown"
        )
        
        # Verify embeddings method was called
        mock_gen.add_embeddings_to_chunks.assert_called_once()
    
    def test_process_directory(self):
        """Test processing a directory of documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = [
                ("doc1.md", "# Document 1\n\nContent 1"),
                ("doc2.md", "# Document 2\n\nContent 2"),
                ("subdir/doc3.md", "# Document 3\n\nContent 3"),
            ]
            
            for filename, content in test_files:
                file_path = Path(tmpdir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Process directory
            chunks = self.chunker.process_directory(
                directory=tmpdir,
                pattern="**/*.md",
                doc_format="markdown"
            )
            
            # Should have chunks from all 3 files
            self.assertGreater(len(chunks), 0)
            stats = self.chunker.get_statistics()
            self.assertEqual(stats['documents_processed'], 3)
    
    def test_process_directory_nonexistent(self):
        """Test error handling for nonexistent directory."""
        with self.assertRaises(ValueError) as context:
            self.chunker.process_directory(
                directory="/nonexistent/path",
                pattern="*.md"
            )
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_process_directory_error_handling(self):
        """Test that directory processing continues on file errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create valid and invalid files
            good_file = Path(tmpdir) / "good.md"
            good_file.write_text("# Good\n\nContent")
            
            bad_file = Path(tmpdir) / "bad.md"
            bad_file.write_text("# Bad")  # Very short, might cause issues
            
            # Process directory
            chunks = self.chunker.process_directory(
                directory=tmpdir,
                pattern="*.md"
            )
            
            # Should have processed at least the good file
            self.assertGreaterEqual(len(chunks), 1)
    
    def test_export_to_json(self):
        """Test exporting chunks to JSON."""
        # Create test chunks
        chunks = self.chunker.process_document(
            content="# Test\n\nContent here.",
            source_path="test.md",
            doc_format="markdown"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"
            
            self.chunker.export_to_json(
                chunks=chunks,
                output_path=str(output_path),
                include_embeddings=False
            )
            
            # Verify file was created
            self.assertTrue(output_path.exists())
            
            # Verify JSON content
            with output_path.open('r') as f:
                data = json.load(f)
            
            self.assertEqual(len(data), len(chunks))
            self.assertIn('chunk_id', data[0])
            self.assertIn('content', data[0])
            self.assertIn('metadata', data[0])
    
    def test_export_to_json_with_embeddings(self):
        """Test exporting chunks with embeddings."""
        chunks = self.chunker.process_document(
            content="# Test\n\nContent.",
            source_path="test.md",
            doc_format="markdown"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output_with_emb.json"
            
            self.chunker.export_to_json(
                chunks=chunks,
                output_path=str(output_path),
                include_embeddings=True
            )
            
            # Verify file was created
            self.assertTrue(output_path.exists())
            
            # Verify JSON is valid
            with output_path.open('r') as f:
                data = json.load(f)
            
            self.assertGreater(len(data), 0)
    
    def test_export_creates_parent_directories(self):
        """Test that export creates parent directories if needed."""
        chunks = self.chunker.process_document(
            content="# Test\n\nContent.",
            source_path="test.md",
            doc_format="markdown"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "nested" / "output.json"
            
            self.chunker.export_to_json(
                chunks=chunks,
                output_path=str(output_path)
            )
            
            self.assertTrue(output_path.exists())
    
    def test_error_statistics(self):
        """Test that errors are recorded in statistics."""
        # Try to process invalid content that will cause an error
        try:
            self.chunker.process_document(
                content="test",
                source_path="test.txt",
                doc_format="invalid_format"
            )
        except ValueError:
            pass
        
        stats = self.chunker.get_statistics()
        self.assertGreater(stats['error_count'], 0)
        self.assertGreater(len(stats['errors']), 0)


class TestUserManualChunkerIntegration(unittest.TestCase):
    """Integration tests for the full pipeline."""
    
    def test_end_to_end_markdown(self):
        """Test complete end-to-end processing of markdown."""
        config = ChunkerConfig(
            max_chunk_size=300,
            min_chunk_size=50,
            generate_summaries=False,
            generate_embeddings=False
        )
        chunker = UserManualChunker(config=config)
        
        markdown = """# User Guide

Welcome to our application.

## Getting Started

### Installation

To install, run:

```bash
pip install myapp
```

### Configuration

Edit the config file:

```yaml
app:
  name: myapp
  port: 8080
```

## Usage

Here's how to use the app:

1. Start the server
2. Open your browser
3. Navigate to localhost:8080

## Advanced Features

### API Integration

Use our REST API:

```python
import requests
response = requests.get('http://localhost:8080/api/data')
```
"""
        
        chunks = chunker.process_document(
            content=markdown,
            source_path="user_guide.md",
            doc_format="markdown"
        )
        
        # Verify chunks were created
        self.assertGreater(len(chunks), 0)
        
        # Verify each chunk has required fields
        for chunk in chunks:
            self.assertIsNotNone(chunk.chunk_id)
            self.assertIsNotNone(chunk.content)
            self.assertIsNotNone(chunk.metadata)
            self.assertIsNotNone(chunk.metadata.source_file)
            self.assertIsNotNone(chunk.metadata.heading_hierarchy)
            self.assertIsInstance(chunk.metadata.contains_code, bool)
            self.assertIsInstance(chunk.metadata.code_languages, list)
        
        # Verify statistics
        stats = chunker.get_statistics()
        self.assertEqual(stats['documents_processed'], 1)
        self.assertEqual(stats['chunks_created'], len(chunks))
        self.assertGreater(stats['code_chunks'], 0)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProcessingStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestUserManualChunker))
    suite.addTests(loader.loadTestsFromTestCase(TestUserManualChunkerIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(run_tests())
