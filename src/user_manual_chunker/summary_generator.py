"""
Summary generator for user manual documentation chunks.

Generates concise summaries using LLM-based generation with fallback to
extractive summaries for error cases.
"""

import re
from typing import Optional
from .data_models import ChunkMetadata
from .interfaces import DocumentChunk


class SummaryGenerator:
    """Generate concise summaries for documentation chunks."""
    
    def __init__(
        self,
        model: str = "iflow/qwen3-coder-plus",
        max_summary_length: int = 150,
        timeout: int = 30
    ):
        """
        Initialize summary generator.
        
        Args:
            model: Model to use for LLM-based summaries
            max_summary_length: Maximum length of generated summaries in words
            timeout: Timeout for LLM requests in seconds
        """
        self.model = model
        self.max_summary_length = max_summary_length
        self.timeout = timeout
        
    def generate_summary(
        self,
        chunk: DocumentChunk,
        doc_context: str,
        metadata: ChunkMetadata
    ) -> str:
        """
        Generate summary using LLM with fallback to extractive summary.
        
        Args:
            chunk: Document chunk to summarize
            doc_context: Context about the overall document
            metadata: Chunk metadata for context
            
        Returns:
            Generated summary string
        """
        try:
            # Try LLM-based summary first
            summary = self._generate_llm_summary(chunk, doc_context, metadata)
            
            # Enforce length constraint
            summary = self._enforce_length_limit(summary)
            
            return summary
            
        except Exception as e:
            print(f"Warning: LLM summary generation failed: {e}")
            # Fall back to extractive summary
            return self._fallback_summary(chunk, metadata)
    
    def _generate_llm_summary(
        self,
        chunk: DocumentChunk,
        doc_context: str,
        metadata: ChunkMetadata
    ) -> str:
        """
        Generate summary using LLM.
        
        Args:
            chunk: Document chunk
            doc_context: Document context
            metadata: Chunk metadata
            
        Returns:
            LLM-generated summary
        """
        # Import here to avoid circular dependency
        from src.iflow_client import create_chat_completion_iflow
        
        # Build documentation-specific prompt
        prompt = self._build_documentation_prompt(chunk, doc_context, metadata)
        
        # Call LLM with timeout
        response = create_chat_completion_iflow(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.3,
            max_tokens=self.max_summary_length * 2  # Allow some buffer
        )
        
        summary = response["choices"][0]["message"]["content"].strip()
        
        # Clean up markdown formatting
        summary = summary.replace("**", "").replace("*", "")
        
        # Remove "Summary:" prefix if present
        summary = re.sub(r'^Summary:\s*', '', summary, flags=re.IGNORECASE)
        
        return summary
    
    def _build_documentation_prompt(
        self,
        chunk: DocumentChunk,
        doc_context: str,
        metadata: ChunkMetadata
    ) -> str:
        """
        Build documentation-specific prompt for LLM.
        
        Args:
            chunk: Document chunk
            doc_context: Document context
            metadata: Chunk metadata
            
        Returns:
            Formatted prompt string
        """
        # Get heading hierarchy for context
        heading_path = " > ".join(metadata.heading_hierarchy) if metadata.heading_hierarchy else "Unknown Section"
        
        # Truncate chunk content if too long
        content = chunk.content
        if len(content) > 2000:
            content = content[:2000] + "\n... (truncated)"
        
        # Check if chunk contains code
        has_code = metadata.contains_code
        code_languages = ", ".join(metadata.code_languages) if metadata.code_languages else "unknown"
        
        # Build prompt based on content type
        if has_code:
            prompt = f"""You are analyzing a section from a technical user manual or documentation.

Document Context: {doc_context}
Section: {heading_path}
Contains Code: Yes ({code_languages})

Content:
{content}

Provide a concise 1-2 sentence summary of this documentation section.
Focus on:
- What concept, feature, or API is being explained
- The purpose of any code examples shown
- Key technical details or parameters
- How this relates to the broader documentation topic

Be specific and mention the code examples if present.

Summary:"""
        else:
            prompt = f"""You are analyzing a section from a technical user manual or documentation.

Document Context: {doc_context}
Section: {heading_path}

Content:
{content}

Provide a concise 1-2 sentence summary of this documentation section.
Focus on:
- What concept, feature, or topic is being explained
- Key information or instructions provided
- How this relates to the broader documentation topic

Be specific and informative.

Summary:"""
        
        return prompt
    
    def _fallback_summary(
        self,
        chunk: DocumentChunk,
        metadata: ChunkMetadata
    ) -> str:
        """
        Generate extractive summary as fallback.
        
        Args:
            chunk: Document chunk
            metadata: Chunk metadata
            
        Returns:
            Extractive summary string
        """
        content = chunk.content.strip()
        
        # Try to extract first meaningful sentence
        sentences = re.split(r'[.!?]\s+', content)
        
        # Filter out very short sentences and headings
        meaningful_sentences = [
            s.strip() for s in sentences 
            if len(s.strip()) > 20 and not s.strip().startswith('#')
        ]
        
        if meaningful_sentences:
            # Use first sentence
            summary = meaningful_sentences[0]
            
            # Add code mention if present
            if metadata.contains_code:
                code_langs = ", ".join(metadata.code_languages) if metadata.code_languages else "code"
                summary += f" Includes {code_langs} examples."
            
            # Enforce length limit
            summary = self._enforce_length_limit(summary)
            return summary
        
        # If no good sentences, use heading hierarchy
        if metadata.heading_hierarchy:
            heading = metadata.heading_hierarchy[-1]
            if metadata.contains_code:
                return f"Documentation for {heading} with code examples."
            else:
                return f"Documentation for {heading}."
        
        # Last resort
        if metadata.contains_code:
            return "Technical documentation section with code examples."
        else:
            return "Technical documentation section."
    
    def _enforce_length_limit(self, summary: str) -> str:
        """
        Enforce maximum summary length.
        
        Args:
            summary: Summary text
            
        Returns:
            Truncated summary if needed
        """
        words = summary.split()
        
        if len(words) <= self.max_summary_length:
            return summary
        
        # Truncate to max length
        truncated = ' '.join(words[:self.max_summary_length])
        
        # Try to end at a sentence boundary
        last_period = truncated.rfind('.')
        if last_period > len(truncated) * 0.7:  # If period is in last 30%
            return truncated[:last_period + 1]
        
        # Otherwise just add ellipsis
        return truncated + "..."


def test_summary_generator():
    """Test the summary generator with sample documentation."""
    from .data_models import Section, Heading, Paragraph, CodeBlock
    
    # Create sample chunk with code
    heading = Heading(level=2, text="Device Initialization", line_number=10)
    
    paragraphs = [
        Paragraph(
            content="The device must be initialized before use. Call the init() method to configure registers.",
            line_start=11,
            line_end=11
        )
    ]
    
    code_blocks = [
        CodeBlock(
            content="device.init()\ndevice.configure(mode='async')",
            language="python",
            line_start=13,
            line_end=14
        )
    ]
    
    section = Section(
        heading=heading,
        paragraphs=paragraphs,
        code_blocks=code_blocks
    )
    
    chunk = DocumentChunk(
        content=section.get_text_content(),
        section=section,
        chunk_index=0,
        line_start=10,
        line_end=14
    )
    
    metadata = ChunkMetadata(
        source_file="manual.md",
        heading_hierarchy=["User Guide", "Device Initialization"],
        section_level=2,
        contains_code=True,
        code_languages=["python"],
        chunk_index=0,
        line_start=10,
        line_end=14,
        char_count=len(chunk.content)
    )
    
    # Test summary generation
    generator = SummaryGenerator(max_summary_length=50)
    
    print("Testing summary generation...")
    print(f"Chunk content:\n{chunk.content}\n")
    
    # Test fallback summary (without LLM)
    print("Testing fallback summary...")
    fallback = generator._fallback_summary(chunk, metadata)
    print(f"Fallback summary: {fallback}\n")
    
    # Test LLM summary (if API key available)
    try:
        doc_context = "Simics Device Modeling Language Reference Manual"
        summary = generator.generate_summary(chunk, doc_context, metadata)
        print(f"LLM summary: {summary}")
    except Exception as e:
        print(f"LLM summary test skipped: {e}")


if __name__ == "__main__":
    test_summary_generator()
