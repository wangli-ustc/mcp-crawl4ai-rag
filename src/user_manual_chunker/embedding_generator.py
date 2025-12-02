"""
Embedding generator for user manual chunks.

Generates vector embeddings for document chunks using the existing
embedding infrastructure (Copilot API).
"""

import numpy as np
from typing import List, Optional
import sys
import os

# Add parent directory to path to import copilot_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from copilot_client import create_embeddings_batch_copilot, create_embedding_copilot
from .interfaces import DocumentChunk
from .data_models import ProcessedChunk


class EmbeddingGenerator:
    """
    Generates embeddings for document chunks.
    
    Integrates with existing embedding infrastructure (Copilot API),
    implements batch processing for efficiency, preserves code syntax,
    and normalizes vectors for cosine similarity.
    """
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        batch_size: int = 32,
        normalize: bool = True
    ):
        """
        Initialize the embedding generator.
        
        Args:
            model: Embedding model to use (default: text-embedding-3-small)
            batch_size: Number of chunks to process in each batch
            normalize: Whether to normalize vectors for cosine similarity
        """
        self.model = model
        self.batch_size = batch_size
        self.normalize = normalize
    
    def generate_embeddings(
        self,
        chunks: List[DocumentChunk]
    ) -> List[np.ndarray]:
        """
        Generate embeddings for a list of chunks in batches.
        
        Args:
            chunks: List of DocumentChunk objects to embed
            
        Returns:
            List of embedding vectors as numpy arrays
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        if not chunks:
            return []
        
        # Extract text content from chunks, preserving code syntax
        texts = [self._prepare_text_for_embedding(chunk) for chunk in chunks]
        
        # Generate embeddings in batches
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            
            try:
                # Use Copilot client for batch embedding
                batch_embeddings = create_embeddings_batch_copilot(batch_texts)
                
                # Convert to numpy arrays
                batch_embeddings_np = [np.array(emb, dtype=np.float32) for emb in batch_embeddings]
                
                # Normalize if requested
                if self.normalize:
                    batch_embeddings_np = self._normalize_vectors(batch_embeddings_np)
                
                all_embeddings.extend(batch_embeddings_np)
                
            except Exception as e:
                raise RuntimeError(f"Failed to generate embeddings for batch {i//self.batch_size + 1}: {e}")
        
        return all_embeddings
    
    def generate_embedding_single(
        self,
        chunk: DocumentChunk
    ) -> np.ndarray:
        """
        Generate embedding for a single chunk.
        
        Args:
            chunk: DocumentChunk to embed
            
        Returns:
            Embedding vector as numpy array
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        text = self._prepare_text_for_embedding(chunk)
        
        try:
            # Use Copilot client for single embedding
            embedding = create_embedding_copilot(text)
            
            # Convert to numpy array
            embedding_np = np.array(embedding, dtype=np.float32)
            
            # Normalize if requested
            if self.normalize:
                embedding_np = self._normalize_vector(embedding_np)
            
            return embedding_np
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")
    
    def _prepare_text_for_embedding(self, chunk: DocumentChunk) -> str:
        """
        Prepare chunk text for embedding, preserving code syntax.
        
        Code blocks are preserved with their language markers to maintain
        syntax information in the embedding.
        
        Args:
            chunk: DocumentChunk to prepare
            
        Returns:
            Text string ready for embedding
        """
        # The chunk content already includes code blocks with proper formatting
        # from the Section.get_text_content() method, which preserves code syntax
        # with triple backticks and language identifiers
        return chunk.content
    
    def _normalize_vectors(
        self,
        embeddings: List[np.ndarray]
    ) -> List[np.ndarray]:
        """
        Normalize embedding vectors for cosine similarity.
        
        Each vector is normalized to unit length (L2 norm = 1.0).
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            List of normalized embedding vectors
        """
        normalized = []
        for emb in embeddings:
            normalized.append(self._normalize_vector(emb))
        return normalized
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize a single vector to unit length.
        
        Args:
            vector: Embedding vector to normalize
            
        Returns:
            Normalized vector with L2 norm = 1.0
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            # Return zero vector if input is zero
            return vector
        return vector / norm
    
    def add_embeddings_to_chunks(
        self,
        chunks: List[DocumentChunk],
        processed_chunks: List[ProcessedChunk]
    ) -> None:
        """
        Generate embeddings and add them to ProcessedChunk objects.
        
        This is a convenience method that generates embeddings for chunks
        and updates the corresponding ProcessedChunk objects in-place.
        
        Args:
            chunks: List of DocumentChunk objects
            processed_chunks: List of ProcessedChunk objects to update
            
        Raises:
            ValueError: If chunks and processed_chunks have different lengths
            RuntimeError: If embedding generation fails
        """
        if len(chunks) != len(processed_chunks):
            raise ValueError(
                f"Mismatch between chunks ({len(chunks)}) and "
                f"processed_chunks ({len(processed_chunks)})"
            )
        
        # Generate all embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Add embeddings to processed chunks
        for processed_chunk, embedding in zip(processed_chunks, embeddings):
            processed_chunk.embedding = embedding
