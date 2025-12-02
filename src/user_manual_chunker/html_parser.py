"""
HTML parser implementation for user manual chunking.

Parses HTML documents to extract structure including headings,
paragraphs, and code blocks.
"""

from typing import List, Optional
from .interfaces import DocumentParser
from .data_models import (
    DocumentStructure,
    Heading,
    CodeBlock,
    Paragraph,
)

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class HTMLParser(DocumentParser):
    """Parser for HTML documents using BeautifulSoup."""
    
    def __init__(self):
        """Initialize the HTML parser."""
        if not BS4_AVAILABLE:
            raise ImportError(
                "BeautifulSoup4 is required for HTML parsing. "
                "Install it with: pip install beautifulsoup4 lxml"
            )
    
    def parse(self, content: str, source_path: str = "") -> DocumentStructure:
        """
        Parse HTML content into structured representation.
        
        Args:
            content: Raw HTML content as string
            source_path: Path to source file for metadata
            
        Returns:
            DocumentStructure with parsed headings, paragraphs, and code blocks
        """
        soup = BeautifulSoup(content, 'lxml')
        
        headings = self.extract_headings(content)
        code_blocks = self.extract_code_blocks(content)
        paragraphs = self._extract_paragraphs(soup, headings, code_blocks)
        
        return DocumentStructure(
            source_path=source_path,
            headings=headings,
            paragraphs=paragraphs,
            code_blocks=code_blocks,
            raw_content=content
        )
    
    def extract_headings(self, content: str) -> List[Heading]:
        """
        Extract heading hierarchy from HTML document.
        
        Args:
            content: Raw HTML content
            
        Returns:
            List of Heading objects with parent relationships
        """
        soup = BeautifulSoup(content, 'lxml')
        headings = []
        
        # Find all heading tags (h1-h6)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(tag.name[1])  # Extract number from h1, h2, etc.
            text = tag.get_text(strip=True)
            
            # Calculate line number by counting newlines before this tag
            line_number = self._calculate_line_number(content, str(tag))
            
            heading = Heading(
                level=level,
                text=text,
                line_number=line_number,
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
        
        Handles <pre><code> and <code> tags.
        
        Args:
            content: Raw HTML content
            
        Returns:
            List of CodeBlock objects with language and location info
        """
        soup = BeautifulSoup(content, 'lxml')
        code_blocks = []
        
        # Find all <pre> tags that contain <code> tags
        for pre_tag in soup.find_all('pre'):
            code_tag = pre_tag.find('code')
            
            if code_tag:
                # Extract code content
                code_content = code_tag.get_text()
                
                # Try to detect language from class attribute
                language = self._detect_language_from_tag(code_tag)
                
                # Calculate line numbers
                line_start = self._calculate_line_number(content, str(pre_tag))
                line_end = line_start + code_content.count('\n')
                
                # Get preceding text
                preceding_text = self._get_preceding_text(pre_tag)
                
                code_blocks.append(CodeBlock(
                    content=code_content,
                    language=language,
                    line_start=line_start,
                    line_end=line_end,
                    preceding_text=preceding_text
                ))
            else:
                # <pre> without <code> - treat as code block
                code_content = pre_tag.get_text()
                
                line_start = self._calculate_line_number(content, str(pre_tag))
                line_end = line_start + code_content.count('\n')
                
                preceding_text = self._get_preceding_text(pre_tag)
                
                code_blocks.append(CodeBlock(
                    content=code_content,
                    language="text",
                    line_start=line_start,
                    line_end=line_end,
                    preceding_text=preceding_text
                ))
        
        # Also find standalone <code> tags (inline code in paragraphs)
        # We'll skip these as they're typically inline, not blocks
        
        return code_blocks
    
    def _detect_language_from_tag(self, tag: 'Tag') -> str:
        """
        Detect programming language from tag attributes.
        
        Common patterns:
        - class="language-python"
        - class="python"
        - data-language="python"
        
        Args:
            tag: BeautifulSoup tag to analyze
            
        Returns:
            Language identifier string
        """
        # Check class attribute
        classes = tag.get('class', [])
        for cls in classes:
            if isinstance(cls, str):
                # Handle "language-python" pattern
                if cls.startswith('language-'):
                    return cls.replace('language-', '')
                # Handle "lang-python" pattern
                if cls.startswith('lang-'):
                    return cls.replace('lang-', '')
                # Handle direct language name
                if cls in ['python', 'javascript', 'java', 'c', 'cpp', 'dml', 
                          'bash', 'shell', 'sql', 'html', 'css', 'json', 'xml']:
                    return cls
        
        # Check data-language attribute
        data_lang = tag.get('data-language')
        if data_lang:
            return data_lang
        
        return "text"
    
    def _calculate_line_number(self, content: str, tag_str: str) -> int:
        """
        Calculate the line number where a tag appears in the content.
        
        Args:
            content: Full HTML content
            tag_str: String representation of the tag
            
        Returns:
            Line number (1-indexed)
        """
        # Find the position of the tag in the content
        # This is approximate since BeautifulSoup may format differently
        try:
            pos = content.find(tag_str[:50])  # Use first 50 chars for matching
            if pos == -1:
                # Try to find by tag name
                return 1
            return content[:pos].count('\n') + 1
        except:
            return 1
    
    def _get_preceding_text(self, tag: 'Tag') -> Optional[str]:
        """
        Get the paragraph immediately preceding a code block.
        
        Args:
            tag: BeautifulSoup tag (pre or code)
            
        Returns:
            Preceding paragraph text or None
        """
        # Look for previous sibling that is a paragraph
        prev_sibling = tag.find_previous_sibling()
        
        while prev_sibling:
            if isinstance(prev_sibling, Tag):
                if prev_sibling.name == 'p':
                    return prev_sibling.get_text(strip=True)
                # Stop at headings
                if prev_sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
            prev_sibling = prev_sibling.find_previous_sibling()
        
        return None
    
    def _extract_paragraphs(
        self,
        soup: BeautifulSoup,
        headings: List[Heading],
        code_blocks: List[CodeBlock]
    ) -> List[Paragraph]:
        """
        Extract paragraphs from HTML content.
        
        Paragraphs are text blocks in <p> tags that are not part of code blocks.
        
        Args:
            soup: BeautifulSoup parsed HTML
            headings: List of extracted headings
            code_blocks: List of extracted code blocks
            
        Returns:
            List of Paragraph objects
        """
        paragraphs = []
        
        # Build set of line numbers that are code blocks
        code_block_lines = set()
        for cb in code_blocks:
            for line_num in range(cb.line_start, cb.line_end + 1):
                code_block_lines.add(line_num)
        
        # Extract all <p> tags
        for p_tag in soup.find_all('p'):
            text = p_tag.get_text(strip=True)
            
            # Skip empty paragraphs
            if not text:
                continue
            
            # Calculate line numbers
            line_start = self._calculate_line_number(
                soup.prettify(),
                str(p_tag)
            )
            line_end = line_start + text.count('\n')
            
            # Skip if this paragraph overlaps with a code block
            if any(line_start <= line <= line_end for line in code_block_lines):
                continue
            
            paragraphs.append(Paragraph(
                content=text,
                line_start=line_start,
                line_end=line_end
            ))
        
        return paragraphs
