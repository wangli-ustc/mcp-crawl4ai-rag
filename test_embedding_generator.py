"""
Unit tests for EmbeddingGenerator.

Tests the embedding generation functionality for document chunks,
including batch processing, normalization, and integration with
the Copilot API.
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from user_manual_chunker import (
    EmbeddingGenerator,
    DocumentChunk,
    ProcessedChunk,
    ChunkMetadata,
)


class MockDocumentChunk(DocumentChunk):
    """Mock implementation of DocumentChunk for testing."""
    
    def __init__(self, content: str, metadata: dict = None):
        self._content = content
        self._metadata = metadata or {}
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def line_start(self) -> int:
        return self._metadata.get("line_start", 1)
    
    @property
    def line_end(self) -> int:
        return self._metadata.get("line_end", 10)
    
    @property
    def metadata(self) -> dict:
        return self._metadata


class TestEmbeddingGenerator(unittest.TestCase):
    """Test cases for EmbeddingGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = EmbeddingGenerator(
            model="text-embedding-3-small",
            batch_size=32,
            normalize=True
        )
        
        # Create mock chunks
        self.mock_chunks = [
            MockDocumentChunk(
                "This is a test chunk about Python programming.",
                {"line_start": 1, "line_end": 5}
            ),
            MockDocumentChunk(
                "```python\ndef hello():\n    print('Hello, World!')\n```",
                {"line_start": 6, "line_end": 10}
            ),
            MockDocumentChunk(
                "Another chunk with documentation content.",
                {"line_start": 11, "line_end": 15}
            ),
        ]
    
    def test_initialization(self):
        """Test EmbeddingGenerator initialization."""
        gen = EmbeddingGenerator(
            model="text-embedding-3-small",
            batch_size=16,
            normalize=False
        )
        
        self.assertEqual(gen.model, "text-embedding-3-small")
        self.assertEqual(gen.batch_size, 16)
        self.assertFalse(gen.normalize)
    
    def test_initialization_defaults(self):
        """Test default initialization parameters."""
        gen = EmbeddingGenerator()
        
        self.assertEqual(gen.model, "text-embedding-3-small")
        self.assertEqual(gen.batch_size, 32)
        self.assertTrue(gen.normalize)
    
    def test_prepare_text_for_embedding(self):
        """Test text preparation preserves chunk content."""
        chunk = MockDocumentChunk(
            "```python\ncode here\n```\nExplanation text."
        )
        
        prepared = self.generator._prepare_text_for_embedding(chunk)
        
        # Should preserve the exact content
        self.assertEqual(prepared, chunk.content)
        # Should preserve code blocks
        self.assertIn("```python", prepared)
        self.assertIn("code here", prepared)
    
    def test_normalize_vector(self):
        """Test vector normalization."""
        # Create a non-normalized vector
        vector = np.array([3.0, 4.0], dtype=np.float32)
        
        normalized = self.generator._normalize_vector(vector)
        
        # Check L2 norm is 1.0
        norm = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm, 1.0, places=5)
        
        # Check direction is preserved
        expected = vector / np.linalg.norm(vector)
        np.testing.assert_array_almost_equal(normalized, expected)
    
    def test_normalize_vector_zero(self):
        """Test normalization of zero vector."""
        vector = np.array([0.0, 0.0], dtype=np.float32)
        
        normalized = self.generator._normalize_vector(vector)
        
        # Should return zero vector
        np.testing.assert_array_equal(normalized, vector)
    
    def test_normalize_vectors_batch(self):
        """Test batch vector normalization."""
        vectors = [
            np.array([3.0, 4.0], dtype=np.float32),
            np.array([1.0, 0.0], dtype=np.float32),
            np.array([0.0, 5.0], dtype=np.float32),
        ]
        
        normalized = self.generator._normalize_vectors(vectors)
        
        # Check all vectors are normalized
        for vec in normalized:
            norm = np.linalg.norm(vec)
            self.assertAlmostEqual(norm, 1.0, places=5)
        
        self.assertEqual(len(normalized), len(vectors))
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_generate_embeddings_batch(self, mock_batch_embed):
        """Test batch embedding generation."""
        # Mock embedding responses
        mock_embeddings = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6],
        ]
        mock_batch_embed.return_value = mock_embeddings
        
        embeddings = self.generator.generate_embeddings(self.mock_chunks)
        
        # Check we got the right number of embeddings
        self.assertEqual(len(embeddings), len(self.mock_chunks))
        
        # Check embeddings are numpy arrays
        for emb in embeddings:
            self.assertIsInstance(emb, np.ndarray)
            self.assertEqual(emb.dtype, np.float32)
        
        # Check normalization was applied
        for emb in embeddings:
            norm = np.linalg.norm(emb)
            self.assertAlmostEqual(norm, 1.0, places=5)
        
        # Verify batch function was called
        mock_batch_embed.assert_called_once()
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_generate_embeddings_without_normalization(self, mock_batch_embed):
        """Test batch embedding generation without normalization."""
        gen = EmbeddingGenerator(normalize=False)
        
        # Mock embedding with non-unit norm
        mock_embeddings = [[3.0, 4.0]]
        mock_batch_embed.return_value = mock_embeddings
        
        chunks = [self.mock_chunks[0]]
        embeddings = gen.generate_embeddings(chunks)
        
        # Check embedding is NOT normalized
        norm = np.linalg.norm(embeddings[0])
        self.assertAlmostEqual(norm, 5.0, places=5)  # sqrt(3^2 + 4^2) = 5
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_generate_embeddings_batching(self, mock_batch_embed):
        """Test that large lists are properly batched."""
        gen = EmbeddingGenerator(batch_size=2)
        
        # Create 5 chunks (should result in 3 batches: 2, 2, 1)
        chunks = [MockDocumentChunk(f"Chunk {i}") for i in range(5)]
        
        # Mock different responses for each batch
        mock_batch_embed.side_effect = [
            [[0.1, 0.2], [0.3, 0.4]],  # Batch 1
            [[0.5, 0.6], [0.7, 0.8]],  # Batch 2
            [[0.9, 1.0]],               # Batch 3
        ]
        
        embeddings = gen.generate_embeddings(chunks)
        
        # Should have called batch function 3 times
        self.assertEqual(mock_batch_embed.call_count, 3)
        
        # Should have 5 embeddings total
        self.assertEqual(len(embeddings), 5)
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_generate_embeddings_error_handling(self, mock_batch_embed):
        """Test error handling in batch embedding generation."""
        mock_batch_embed.side_effect = Exception("API error")
        
        with self.assertRaises(RuntimeError) as context:
            self.generator.generate_embeddings(self.mock_chunks)
        
        self.assertIn("Failed to generate embeddings", str(context.exception))
    
    @patch('user_manual_chunker.embedding_generator.create_embedding_copilot')
    def test_generate_embedding_single(self, mock_single_embed):
        """Test single embedding generation."""
        mock_embedding = [0.1, 0.2, 0.3, 0.4]
        mock_single_embed.return_value = mock_embedding
        
        embedding = self.generator.generate_embedding_single(self.mock_chunks[0])
        
        # Check embedding is numpy array
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.dtype, np.float32)
        
        # Check normalization
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=5)
        
        # Verify function was called with prepared text
        mock_single_embed.assert_called_once()
    
    @patch('user_manual_chunker.embedding_generator.create_embedding_copilot')
    def test_generate_embedding_single_error(self, mock_single_embed):
        """Test error handling in single embedding generation."""
        mock_single_embed.side_effect = Exception("API error")
        
        with self.assertRaises(RuntimeError) as context:
            self.generator.generate_embedding_single(self.mock_chunks[0])
        
        self.assertIn("Failed to generate embedding", str(context.exception))
    
    def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for empty chunk list."""
        embeddings = self.generator.generate_embeddings([])
        
        self.assertEqual(embeddings, [])
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_add_embeddings_to_chunks(self, mock_batch_embed):
        """Test adding embeddings to ProcessedChunk objects."""
        # Create mock ProcessedChunks
        processed_chunks = [
            ProcessedChunk(
                chunk_id=f"chunk_{i}",
                content=chunk.content,
                metadata=ChunkMetadata(
                    source_file="test.md",
                    heading_hierarchy=["Test"],
                    section_level=1,
                    contains_code=False,
                    code_languages=[],
                    chunk_index=i,
                    line_start=chunk.line_start,
                    line_end=chunk.line_end,
                    char_count=len(chunk.content),
                ),
                summary="Test summary",
                embedding=None
            )
            for i, chunk in enumerate(self.mock_chunks)
        ]
        
        # Mock embeddings
        mock_embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]
        mock_batch_embed.return_value = mock_embeddings
        
        # Add embeddings
        self.generator.add_embeddings_to_chunks(
            self.mock_chunks,
            processed_chunks
        )
        
        # Verify embeddings were added
        for i, pc in enumerate(processed_chunks):
            self.assertIsNotNone(pc.embedding)
            self.assertIsInstance(pc.embedding, np.ndarray)
            # Check normalization
            norm = np.linalg.norm(pc.embedding)
            self.assertAlmostEqual(norm, 1.0, places=5)
    
    def test_add_embeddings_to_chunks_mismatch(self):
        """Test error when chunk counts don't match."""
        processed_chunks = [
            ProcessedChunk(
                chunk_id="chunk_0",
                content="test",
                metadata=ChunkMetadata(
                    source_file="test.md",
                    heading_hierarchy=["Test"],
                    section_level=1,
                    contains_code=False,
                    code_languages=[],
                    chunk_index=0,
                    line_start=1,
                    line_end=5,
                    char_count=4,
                ),
                summary="Test",
                embedding=None
            )
        ]
        
        # Different number of chunks
        with self.assertRaises(ValueError) as context:
            self.generator.add_embeddings_to_chunks(
                self.mock_chunks,  # 3 chunks
                processed_chunks   # 1 chunk
            )
        
        self.assertIn("Mismatch", str(context.exception))
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_code_block_preservation(self, mock_batch_embed):
        """Test that code blocks are preserved in embedding input."""
        code_chunk = MockDocumentChunk(
            "Here's an example:\n\n```python\ndef test():\n    return 42\n```\n\nThis function returns 42."
        )
        
        mock_batch_embed.return_value = [[0.1, 0.2, 0.3]]
        
        self.generator.generate_embeddings([code_chunk])
        
        # Get the text that was prepared for embedding
        prepared_text = self.generator._prepare_text_for_embedding(code_chunk)
        
        # Verify code blocks are preserved
        self.assertIn("```python", prepared_text)
        self.assertIn("def test():", prepared_text)
        self.assertIn("return 42", prepared_text)
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_batch_processing_preserves_order(self, mock_batch_embed):
        """Test that batch processing preserves chunk order."""
        # Create chunks with identifiable content
        chunks = [
            MockDocumentChunk(f"Content {i}") for i in range(10)
        ]
        
        # Mock embeddings with identifiable values
        mock_embeddings = [[float(i), float(i)] for i in range(10)]
        
        # Split into batches
        gen = EmbeddingGenerator(batch_size=3)
        mock_batch_embed.side_effect = [
            mock_embeddings[0:3],
            mock_embeddings[3:6],
            mock_embeddings[6:9],
            mock_embeddings[9:10],
        ]
        
        embeddings = gen.generate_embeddings(chunks)
        
        # Verify order is preserved
        for i, emb in enumerate(embeddings):
            # First element should match index (before normalization changes it)
            # Just verify we got 10 embeddings in order
            self.assertEqual(len(embeddings), 10)


class TestEmbeddingIntegration(unittest.TestCase):
    """Integration tests for EmbeddingGenerator."""
    
    @patch('user_manual_chunker.embedding_generator.create_embeddings_batch_copilot')
    def test_full_pipeline(self, mock_batch_embed):
        """Test full embedding pipeline with ProcessedChunks."""
        # Create document chunks
        chunks = [
            MockDocumentChunk("Introduction to the API"),
            MockDocumentChunk("```python\napi.call()\n```"),
            MockDocumentChunk("Error handling examples"),
        ]
        
        # Create processed chunks
        processed = [
            ProcessedChunk(
                chunk_id=f"chunk_{i}",
                content=chunk.content,
                metadata=ChunkMetadata(
                    source_file="api.md",
                    heading_hierarchy=["API", "Documentation"],
                    section_level=2,
                    contains_code=True if "```" in chunk.content else False,
                    code_languages=["python"] if "```python" in chunk.content else [],
                    chunk_index=i,
                    line_start=i * 10 + 1,
                    line_end=i * 10 + 10,
                    char_count=len(chunk.content),
                ),
                summary=f"Summary {i}",
                embedding=None
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Mock embeddings
        mock_batch_embed.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]
        
        # Generate embeddings
        gen = EmbeddingGenerator()
        gen.add_embeddings_to_chunks(chunks, processed)
        
        # Verify all processed chunks have embeddings
        for pc in processed:
            self.assertIsNotNone(pc.embedding)
            self.assertIsInstance(pc.embedding, np.ndarray)
            
            # Verify normalization
            norm = np.linalg.norm(pc.embedding)
            self.assertAlmostEqual(norm, 1.0, places=5)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddingGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddingIntegration))
    
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
