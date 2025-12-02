"""
Markdown parser implementation for user manual chunking.

Parses markdown documents to extract structure including headings,
paragraphs, and code blocks.
"""

import re
from typing import List, Optional, Tuple
from .interfaces import DocumentParser
from .data_models import (
    DocumentStructure,
    Heading,
    CodeBlock,
    Paragraph,
)


class MarkdownParser(DocumentParser):
    """Parser for markdown documents."""
    
    # Regex patterns for markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[^}]+\})?$', re.MULTILINE)
    CODE_FENCE_PATTERN = re.compile(
        r'^```(\w*)\s*\n(.*?)^```\s*$',
        re.MULTILINE | re.DOTALL
    )
    INDENTED_CODE_PATTERN = re.compile(
        r'^((?:    |\t).*(?:\n(?:    |\t).*|\n)*)',
        re.MULTILINE
    )
    
    def parse(self, content: str, source_path: str = "") -> DocumentStructure:
        """
        Parse markdown content into structured representation.
        
        Args:
            content: Raw markdown content as string
            source_path: Path to source file for metadata
            
        Returns:
            DocumentStructure with parsed headings, paragraphs, and code blocks
        """
        headings = self.extract_headings(content)
        code_blocks = self.extract_code_blocks(content)
        paragraphs = self._extract_paragraphs(content, headings, code_blocks)
        
        return DocumentStructure(
            source_path=source_path,
            headings=headings,
            paragraphs=paragraphs,
            code_blocks=code_blocks,
            raw_content=content
        )
    
    def extract_headings(self, content: str) -> List[Heading]:
        """
        Extract heading hierarchy from markdown document.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of Heading objects with parent relationships
        """
        headings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            match = self.HEADING_PATTERN.match(line)
            if match:
                level = len(match.group(1))  # Count the # symbols
                text = match.group(2).strip()
                
                heading = Heading(
                    level=level,
                    text=text,
                    line_number=line_num,
                    parent=None
                )
                headings.append(heading)
        
        # Build parent relationships
        self._build_heading_hierarchy(headings)
        
        return headings
    
    def _build_heading_hierarchy(self, headings: List[Heading]) -> None:
        """
        Build parent-child relationships between headings.
        
        Args:
            headings: List of headings to process (modified in place)
        """
        # Stack to track the current hierarchy
        stack: List[Heading] = []
        
        for heading in headings:
            # Pop headings from stack that are at same or deeper level
            while stack and stack[-1].level >= heading.level:
                stack.pop()
            
            # The top of stack is now the parent (if any)
            if stack:
                heading.parent = stack[-1]
            
            # Add current heading to stack
            stack.append(heading)
    
    def extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """
        Extract code blocks with language information.
        
        Handles both triple-backtick fenced code blocks and indented code blocks.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of CodeBlock objects with language and location info
        """
        code_blocks = []
        lines = content.split('\n')
        
        # Extract fenced code blocks (triple backticks)
        for match in self.CODE_FENCE_PATTERN.finditer(content):
            language = match.group(1) or "text"
            code_content = match.group(2)
            
            # Find line numbers
            start_pos = match.start()
            end_pos = match.end()
            line_start = content[:start_pos].count('\n') + 1
            line_end = content[:end_pos].count('\n') + 1
            
            # Get preceding text (paragraph before code block)
            preceding_text = self._get_preceding_text(content, start_pos, lines)
            
            code_blocks.append(CodeBlock(
                content=code_content,
                language=language,
                line_start=line_start,
                line_end=line_end,
                preceding_text=preceding_text
            ))
        
        # Extract indented code blocks (4 spaces or tab)
        # Only if they're not already captured as fenced blocks
        fenced_ranges = [(cb.line_start, cb.line_end) for cb in code_blocks]
        
        current_block = []
        block_start_line = None
        
        for line_num, line in enumerate(lines, start=1):
            # Check if this line is already in a fenced code block
            in_fenced = any(start <= line_num <= end for start, end in fenced_ranges)
            
            if not in_fenced and (line.startswith('    ') or line.startswith('\t')):
                # This is an indented code line
                if block_start_line is None:
                    block_start_line = line_num
                # Remove the indentation
                code_line = line[4:] if line.startswith('    ') else line[1:]
                current_block.append(code_line)
            else:
                # Not an indented code line
                if current_block:
                    # Save the accumulated block
                    code_content = '\n'.join(current_block)
                    preceding_text = self._get_preceding_text_by_line(
                        lines, block_start_line - 1
                    )
                    
                    code_blocks.append(CodeBlock(
                        content=code_content,
                        language="text",
                        line_start=block_start_line,
                        line_end=line_num - 1,
                        preceding_text=preceding_text
                    ))
                    
                    current_block = []
                    block_start_line = None
        
        # Handle any remaining indented block at end of file
        if current_block:
            code_content = '\n'.join(current_block)
            preceding_text = self._get_preceding_text_by_line(
                lines, block_start_line - 1
            )
            
            code_blocks.append(CodeBlock(
                content=code_content,
                language="text",
                line_start=block_start_line,
                line_end=len(lines),
                preceding_text=preceding_text
            ))
        
        # Sort by line number
        code_blocks.sort(key=lambda cb: cb.line_start)
        
        return code_blocks
    
    def _get_preceding_text(
        self,
        content: str,
        code_start_pos: int,
        lines: List[str]
    ) -> Optional[str]:
        """
        Get the paragraph immediately preceding a code block.
        
        Args:
            content: Full document content
            code_start_pos: Character position where code block starts
            lines: Lines of the document
            
        Returns:
            Preceding paragraph text or None
        """
        # Find the line number where code starts
        line_num = content[:code_start_pos].count('\n')
        
        return self._get_preceding_text_by_line(lines, line_num)
    
    def _get_preceding_text_by_line(
        self,
        lines: List[str],
        code_line_num: int
    ) -> Optional[str]:
        """
        Get the paragraph immediately preceding a code block by line number.
        
        Args:
            lines: Lines of the document
            code_line_num: Line number where code starts (0-indexed)
            
        Returns:
            Preceding paragraph text or None
        """
        if code_line_num <= 0:
            return None
        
        # Look backwards for non-empty lines
        preceding_lines = []
        for i in range(code_line_num - 1, -1, -1):
            line = lines[i].strip()
            
            # Stop at empty line or heading
            if not line or line.startswith('#'):
                break
            
            # Stop at another code fence
            if line.startswith('```'):
                break
            
            preceding_lines.insert(0, lines[i])
        
        if preceding_lines:
            return '\n'.join(preceding_lines).strip()
        
        return None
    
    def _extract_paragraphs(
        self,
        content: str,
        headings: List[Heading],
        code_blocks: List[CodeBlock]
    ) -> List[Paragraph]:
        """
        Extract paragraphs from markdown content.
        
        Paragraphs are text blocks that are not headings or code blocks.
        
        Args:
            content: Raw markdown content
            headings: List of extracted headings
            code_blocks: List of extracted code blocks
            
        Returns:
            List of Paragraph objects
        """
        lines = content.split('\n')
        paragraphs = []
        
        # Build sets of line numbers that are headings or code blocks
        heading_lines = {h.line_number for h in headings}
        code_block_lines = set()
        for cb in code_blocks:
            for line_num in range(cb.line_start, cb.line_end + 1):
                code_block_lines.add(line_num)
        
        # Extract paragraphs
        current_para = []
        para_start_line = None
        
        for line_num, line in enumerate(lines, start=1):
            # Skip if this line is a heading or in a code block
            if line_num in heading_lines or line_num in code_block_lines:
                # Save accumulated paragraph
                if current_para:
                    para_text = '\n'.join(current_para).strip()
                    if para_text:  # Only save non-empty paragraphs
                        paragraphs.append(Paragraph(
                            content=para_text,
                            line_start=para_start_line,
                            line_end=line_num - 1
                        ))
                    current_para = []
                    para_start_line = None
                continue
            
            # Check if line is empty
            if not line.strip():
                # Empty line ends current paragraph
                if current_para:
                    para_text = '\n'.join(current_para).strip()
                    if para_text:
                        paragraphs.append(Paragraph(
                            content=para_text,
                            line_start=para_start_line,
                            line_end=line_num - 1
                        ))
                    current_para = []
                    para_start_line = None
            else:
                # Non-empty line, add to current paragraph
                if para_start_line is None:
                    para_start_line = line_num
                current_para.append(line)
        
        # Handle any remaining paragraph at end of file
        if current_para:
            para_text = '\n'.join(current_para).strip()
            if para_text:
                paragraphs.append(Paragraph(
                    content=para_text,
                    line_start=para_start_line,
                    line_end=len(lines)
                ))
        
        return paragraphs
