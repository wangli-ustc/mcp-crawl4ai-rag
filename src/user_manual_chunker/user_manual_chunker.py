"""
Main orchestrator for user manual chunking pipeline.

Coordinates parsing, chunking, metadata extraction, summary generation,
and embedding generation to produce complete ProcessedChunk objects.
"""

import hashlib
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from .interfaces import DocumentParser, SemanticChunker, MetadataExtractor
from .data_models import ProcessedChunk, DocumentStructure, ChunkMetadata
from .config import ChunkerConfig
from .markdown_parser import MarkdownParser
from .html_parser import HTMLParser
from .semantic_chunker import SemanticChunker as SemanticChunkerImpl
from .metadata_extractor import MetadataExtractor as MetadataExtractorImpl
from .summary_generator import SummaryGenerator
from .embedding_generator import EmbeddingGenerator


logger = logging.getLogger(__name__)


class ProcessingStatistics:
    """Statistics for document processing."""
    
    def __init__(self):
        self.documents_processed = 0
        self.chunks_created = 0
        self.total_characters = 0
        self.total_tokens = 0
        self.code_chunks = 0
        self.summaries_generated = 0
        self.embeddings_generated = 0
        self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        avg_chunk_size = (
            self.total_characters / self.chunks_created 
            if self.chunks_created > 0 else 0
        )
        
        return {
            "documents_processed": self.documents_processed,
            "chunks_created": self.chunks_created,
            "total_characters": self.total_characters,
            "total_tokens": self.total_tokens,
            "average_chunk_size": round(avg_chunk_size, 2),
            "code_chunks": self.code_chunks,
            "summaries_generated": self.summaries_generated,
            "embeddings_generated": self.embeddings_generated,
            "error_count": len(self.errors),
            "errors": self.errors[:10]  # Limit to first 10 errors
        }


class UserManualChunker:
    """
    Main orchestrator for the user manual chunking pipeline.
    
    Coordinates all components to process documentation:
    1. Parse document (markdown/HTML)
    2. Chunk into semantic units
    3. Extract metadata
    4. Generate summaries (optional)
    5. Generate embeddings (optional)
    
    Returns complete ProcessedChunk objects ready for storage.
    """
    
    def __init__(
        self,
        config: Optional[ChunkerConfig] = None,
        parser: Optional[DocumentParser] = None,
        chunker: Optional[SemanticChunker] = None,
        metadata_extractor: Optional[MetadataExtractor] = None,
        summary_generator: Optional[SummaryGenerator] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize the user manual chunker.
        
        Args:
            config: Configuration object (defaults to ChunkerConfig())
            parser: Custom document parser (defaults to MarkdownParser)
            chunker: Custom semantic chunker (defaults to SemanticChunkerImpl)
            metadata_extractor: Custom metadata extractor (defaults to MetadataExtractorImpl)
            summary_generator: Custom summary generator (defaults to SummaryGenerator)
            embedding_generator: Custom embedding generator (defaults to EmbeddingGenerator)
        """
        self.config = config or ChunkerConfig()
        self.statistics = ProcessingStatistics()
        
        # Initialize parsers
        self.markdown_parser = MarkdownParser()
        self.html_parser = HTMLParser()
        self.custom_parser = parser
        
        # Initialize components with config
        self.chunker = chunker or SemanticChunkerImpl(
            max_chunk_size=self.config.max_chunk_size,
            min_chunk_size=self.config.min_chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            size_metric=self.config.size_metric
        )
        
        self.metadata_extractor = metadata_extractor or MetadataExtractorImpl()
        
        # Optional components based on config
        self.summary_generator = None
        if self.config.generate_summaries:
            self.summary_generator = summary_generator or SummaryGenerator(
                model=self.config.summary_model,
                max_summary_length=self.config.max_summary_length,
                timeout=self.config.summary_timeout_seconds
            )
        
        self.embedding_generator = None
        if self.config.generate_embeddings:
            self.embedding_generator = embedding_generator or EmbeddingGenerator(
                model=self.config.embedding_model,
                batch_size=self.config.embedding_batch_size,
                normalize=True
            )
        
        logger.info(
            f"UserManualChunker initialized - "
            f"summaries: {self.config.generate_summaries}, "
            f"embeddings: {self.config.generate_embeddings}"
        )
    
    def process_document(
        self,
        content: str,
        source_path: str,
        doc_format: str = "markdown",
        doc_context: Optional[str] = None
    ) -> List[ProcessedChunk]:
        """
        Process a single document end-to-end.
        
        Args:
            content: Document content
            source_path: Source file path for metadata
            doc_format: Document format ('markdown', 'html', or 'custom')
            doc_context: Optional document context for summary generation
        
        Returns:
            List of ProcessedChunk objects with all fields populated
            
        Raises:
            ValueError: If doc_format is invalid or processing fails
        """
        logger.info(f"Processing document: {source_path} (format: {doc_format})")
        
        try:
            # Step 1: Parse document
            doc_structure = self._parse_document(content, source_path, doc_format)
            
            # Step 2: Chunk document
            chunks = self.chunker.chunk_document(doc_structure)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 3: Extract metadata
            chunk_metadatas = []
            for i, chunk in enumerate(chunks):
                # Set chunk index on chunk for metadata extraction
                chunk.chunk_index = i
                metadata = self.metadata_extractor.extract(chunk, doc_structure)
                chunk_metadatas.append(metadata)
            
            # Step 4: Generate summaries (optional)
            summaries = self._generate_summaries(
                chunks,
                chunk_metadatas,
                doc_context or source_path
            )
            
            # Step 5: Create ProcessedChunk objects
            processed_chunks = []
            for i, (chunk, metadata, summary) in enumerate(
                zip(chunks, chunk_metadatas, summaries)
            ):
                chunk_id = self._generate_chunk_id(source_path, i, chunk.content)
                
                processed_chunk = ProcessedChunk(
                    chunk_id=chunk_id,
                    content=chunk.content,
                    metadata=metadata,
                    summary=summary,
                    embedding=None  # To be filled in step 6
                )
                processed_chunks.append(processed_chunk)
            
            # Step 6: Generate embeddings (optional)
            if self.embedding_generator:
                self.embedding_generator.add_embeddings_to_chunks(
                    chunks,
                    processed_chunks
                )
                self.statistics.embeddings_generated += len(processed_chunks)
            
            # Update statistics
            self.statistics.documents_processed += 1
            self.statistics.chunks_created += len(processed_chunks)
            self.statistics.total_characters += sum(m.char_count for m in chunk_metadatas)
            self.statistics.total_tokens += sum(
                m.token_count for m in chunk_metadatas if m.token_count
            )
            self.statistics.code_chunks += sum(1 for m in chunk_metadatas if m.contains_code)
            
            logger.info(f"Successfully processed {source_path}: {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            error_msg = f"Error processing {source_path}: {str(e)}"
            logger.error(error_msg)
            self.statistics.errors.append(error_msg)
            raise ValueError(error_msg) from e
    
    def process_directory(
        self,
        directory: str,
        pattern: str = "**/*.md",
        doc_format: str = "markdown"
    ) -> List[ProcessedChunk]:
        """
        Process all documents in a directory.
        
        Args:
            directory: Directory path
            pattern: Glob pattern for file matching (default: **/*.md)
            doc_format: Document format ('markdown' or 'html')
        
        Returns:
            List of all ProcessedChunk objects from all documents
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        logger.info(f"Processing directory: {directory} (pattern: {pattern})")
        
        all_chunks = []
        files = list(directory_path.glob(pattern))
        
        logger.info(f"Found {len(files)} files matching pattern")
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                chunks = self.process_document(
                    content=content,
                    source_path=str(file_path),
                    doc_format=doc_format
                )
                all_chunks.extend(chunks)
                
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {str(e)}"
                logger.error(error_msg)
                self.statistics.errors.append(error_msg)
                continue
        
        logger.info(
            f"Directory processing complete: "
            f"{len(all_chunks)} chunks from {self.statistics.documents_processed} documents"
        )
        
        return all_chunks
    
    def export_to_json(
        self,
        chunks: List[ProcessedChunk],
        output_path: str,
        include_embeddings: bool = True
    ) -> None:
        """
        Export chunks to JSON format.
        
        Args:
            chunks: List of ProcessedChunk objects
            output_path: Output file path
            include_embeddings: Whether to include embedding vectors (default: True)
        """
        logger.info(f"Exporting {len(chunks)} chunks to {output_path}")
        
        # Convert chunks to dictionaries
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = chunk.to_dict()
            
            # Optionally exclude embeddings for smaller files
            if not include_embeddings and 'embedding' in chunk_dict:
                chunk_dict['embedding'] = None
            
            chunk_dicts.append(chunk_dict)
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported to {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return self.statistics.to_dict()
    
    def reset_statistics(self) -> None:
        """Reset processing statistics."""
        self.statistics = ProcessingStatistics()
        logger.info("Statistics reset")
    
    def _parse_document(
        self,
        content: str,
        source_path: str,
        doc_format: str
    ) -> DocumentStructure:
        """Parse document based on format."""
        if doc_format == "markdown":
            return self.markdown_parser.parse(content, source_path)
        elif doc_format == "html":
            return self.html_parser.parse(content, source_path)
        elif doc_format == "custom" and self.custom_parser:
            return self.custom_parser.parse(content, source_path)
        else:
            raise ValueError(
                f"Invalid document format '{doc_format}'. "
                f"Supported: markdown, html, custom (with custom parser)"
            )
    
    def _generate_summaries(
        self,
        chunks: List,
        metadatas: List[ChunkMetadata],
        doc_context: str
    ) -> List[Optional[str]]:
        """Generate summaries for chunks if enabled."""
        if not self.summary_generator:
            return [None] * len(chunks)
        
        summaries = []
        for chunk, metadata in zip(chunks, metadatas):
            try:
                summary = self.summary_generator.generate_summary(
                    chunk,
                    doc_context,
                    metadata
                )
                summaries.append(summary)
                self.statistics.summaries_generated += 1
                
            except Exception as e:
                logger.warning(f"Summary generation failed: {e}")
                summaries.append(None)
        
        return summaries
    
    def _generate_chunk_id(
        self,
        source_path: str,
        chunk_index: int,
        content: str
    ) -> str:
        """
        Generate unique chunk ID.
        
        Uses combination of source path, chunk index, and content hash
        to ensure uniqueness and deduplication.
        """
        # Create hash of content for deduplication
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        
        # Combine source path (filename only), index, and hash
        path = Path(source_path)
        filename = path.stem  # Filename without extension
        
        return f"{filename}_{chunk_index:04d}_{content_hash}"
