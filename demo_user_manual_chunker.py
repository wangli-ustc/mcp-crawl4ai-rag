"""
Demo script for UserManualChunker.

Demonstrates end-to-end processing of user manuals including:
- Document parsing
- Semantic chunking
- Metadata extraction
- Summary generation
- Embedding generation
- JSON export
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from user_manual_chunker import (
    UserManualChunker,
    ChunkerConfig,
)


def demo_basic_usage():
    """Demonstrate basic usage with minimal configuration."""
    print("=" * 70)
    print("Demo 1: Basic Usage (No Summaries, No Embeddings)")
    print("=" * 70)
    
    # Sample markdown document
    markdown_doc = """# User Guide

Welcome to the application user guide.

## Installation

To install the application, follow these steps:

1. Download the installer
2. Run the installation wizard
3. Follow the on-screen instructions

### System Requirements

- Operating System: Windows 10 or later
- Memory: 4GB RAM minimum
- Disk Space: 500MB free space

## Getting Started

### First Launch

When you first launch the application:

```python
from myapp import Application

app = Application()
app.start()
```

The code above initializes and starts the application.

### Configuration

Edit the configuration file to customize settings:

```yaml
app:
  name: MyApplication
  version: 1.0
  port: 8080
```

## Features

### Feature 1: Data Processing

The application can process large datasets efficiently.

### Feature 2: Visualization

Create beautiful visualizations of your data.

## Troubleshooting

If you encounter issues, try the following:

1. Check the log files
2. Verify your configuration
3. Contact support
"""
    
    # Create chunker with basic configuration
    config = ChunkerConfig(
        max_chunk_size=400,
        min_chunk_size=100,
        chunk_overlap=50,
        generate_summaries=False,
        generate_embeddings=False
    )
    
    chunker = UserManualChunker(config=config)
    
    # Process document
    print("\n1. Processing markdown document...")
    chunks = chunker.process_document(
        content=markdown_doc,
        source_path="user_guide.md",
        doc_format="markdown"
    )
    
    print(f"   ✓ Created {len(chunks)} chunks")
    
    # Show first chunk details
    print("\n2. First chunk details:")
    chunk = chunks[0]
    print(f"   Chunk ID: {chunk.chunk_id}")
    print(f"   Content length: {len(chunk.content)} characters")
    print(f"   Heading hierarchy: {chunk.metadata.heading_hierarchy}")
    print(f"   Contains code: {chunk.metadata.contains_code}")
    print(f"   Code languages: {chunk.metadata.code_languages}")
    print(f"   Lines: {chunk.metadata.line_start}-{chunk.metadata.line_end}")
    print(f"\n   Content preview:")
    print(f"   {chunk.content[:200]}...")
    
    # Show statistics
    print("\n3. Processing statistics:")
    stats = chunker.get_statistics()
    for key, value in stats.items():
        if key != 'errors':  # Skip error list
            print(f"   {key}: {value}")
    
    return chunker, chunks


def demo_with_summaries():
    """Demonstrate usage with summary generation enabled."""
    print("\n\n" + "=" * 70)
    print("Demo 2: With Summary Generation")
    print("=" * 70)
    
    # Note: This demo shows configuration but won't actually generate summaries
    # unless the iFlow API is available
    config = ChunkerConfig(
        max_chunk_size=500,
        generate_summaries=True,  # Enable summaries
        generate_embeddings=False,
        summary_model="iflow/qwen3-coder-plus",
        max_summary_length=100
    )
    
    chunker = UserManualChunker(config=config)
    
    short_doc = """# API Reference

## Authentication

Use API keys for authentication:

```python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get('https://api.example.com/data', headers=headers)
```

## Endpoints

### GET /users

Retrieve list of users.

### POST /users

Create a new user.
"""
    
    print("\n1. Processing with summary generation...")
    print("   (Note: Summaries require API access)")
    
    try:
        chunks = chunker.process_document(
            content=short_doc,
            source_path="api_reference.md",
            doc_format="markdown",
            doc_context="API Reference Documentation"
        )
        
        print(f"   ✓ Created {len(chunks)} chunks")
        
        # Show summaries if generated
        has_summaries = any(chunk.summary for chunk in chunks)
        if has_summaries:
            print("\n2. Generated summaries:")
            for i, chunk in enumerate(chunks):
                if chunk.summary:
                    print(f"   Chunk {i+1}: {chunk.summary}")
        else:
            print("\n2. No summaries generated (API not configured)")
        
        return chunker, chunks
        
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        print("   (This is expected if API is not configured)")
        return None, []


def demo_json_export():
    """Demonstrate JSON export functionality."""
    print("\n\n" + "=" * 70)
    print("Demo 3: JSON Export")
    print("=" * 70)
    
    config = ChunkerConfig(
        max_chunk_size=300,
        generate_summaries=False,
        generate_embeddings=False
    )
    
    chunker = UserManualChunker(config=config)
    
    doc = """# Quick Start

## Step 1: Installation

Install using pip:

```bash
pip install myapp
```

## Step 2: Basic Usage

Import and use:

```python
from myapp import hello
hello()
```
"""
    
    print("\n1. Processing document...")
    chunks = chunker.process_document(
        content=doc,
        source_path="quick_start.md",
        doc_format="markdown"
    )
    
    # Export to JSON
    output_path = "demo_output.json"
    print(f"\n2. Exporting to {output_path}...")
    
    chunker.export_to_json(
        chunks=chunks,
        output_path=output_path,
        include_embeddings=False
    )
    
    print(f"   ✓ Exported {len(chunks)} chunks")
    
    # Read and display JSON structure
    print("\n3. JSON structure:")
    with open(output_path, 'r') as f:
        data = json.load(f)
    
    if data:
        print("   First chunk keys:")
        for key in data[0].keys():
            print(f"   - {key}")
        
        # Show sample metadata
        print("\n   Sample metadata:")
        metadata = data[0]['metadata']
        print(f"   Source: {metadata['source_file']}")
        print(f"   Hierarchy: {metadata['heading_hierarchy']}")
        print(f"   Has code: {metadata['contains_code']}")
    
    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"\n   Cleaned up {output_path}")
    
    return chunker, chunks


def demo_directory_processing():
    """Demonstrate processing multiple files."""
    print("\n\n" + "=" * 70)
    print("Demo 4: Directory Processing")
    print("=" * 70)
    
    import tempfile
    
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n1. Creating test files in {tmpdir}...")
        
        # Create test files
        files = {
            "intro.md": "# Introduction\n\nWelcome to our documentation.",
            "guide.md": "# User Guide\n\n## Getting Started\n\nFollow these steps.",
            "api.md": "# API Reference\n\n## Methods\n\n### get_data()\n\nRetrieve data."
        }
        
        for filename, content in files.items():
            filepath = Path(tmpdir) / filename
            filepath.write_text(content)
        
        print(f"   ✓ Created {len(files)} test files")
        
        # Process directory
        print("\n2. Processing directory...")
        config = ChunkerConfig(
            max_chunk_size=200,
            generate_summaries=False,
            generate_embeddings=False
        )
        
        chunker = UserManualChunker(config=config)
        
        all_chunks = chunker.process_directory(
            directory=tmpdir,
            pattern="*.md",
            doc_format="markdown"
        )
        
        print(f"   ✓ Processed {len(files)} files")
        print(f"   ✓ Created {len(all_chunks)} total chunks")
        
        # Show statistics
        print("\n3. Statistics:")
        stats = chunker.get_statistics()
        print(f"   Documents processed: {stats['documents_processed']}")
        print(f"   Chunks created: {stats['chunks_created']}")
        print(f"   Average chunk size: {stats['average_chunk_size']:.1f} chars")
        
        return chunker, all_chunks


def demo_configuration_options():
    """Demonstrate different configuration options."""
    print("\n\n" + "=" * 70)
    print("Demo 5: Configuration Options")
    print("=" * 70)
    
    test_doc = """# Test Document

## Section 1

Content for section 1 with some text to make it larger.

## Section 2

More content here to test chunking behavior.

```python
def example():
    return "code"
```

## Section 3

Final section with additional content.
"""
    
    configs = [
        ("Small chunks (max=200)", ChunkerConfig(max_chunk_size=200, min_chunk_size=50)),
        ("Large chunks (max=800)", ChunkerConfig(max_chunk_size=800, min_chunk_size=100)),
        ("With overlap (50 chars)", ChunkerConfig(max_chunk_size=400, chunk_overlap=50)),
        ("No overlap", ChunkerConfig(max_chunk_size=400, chunk_overlap=0)),
    ]
    
    for name, config in configs:
        print(f"\n{name}:")
        
        config.generate_summaries = False
        config.generate_embeddings = False
        
        chunker = UserManualChunker(config=config)
        chunks = chunker.process_document(
            content=test_doc,
            source_path="test.md",
            doc_format="markdown"
        )
        
        stats = chunker.get_statistics()
        print(f"   Chunks: {stats['chunks_created']}")
        print(f"   Avg size: {stats['average_chunk_size']:.1f} chars")
        print(f"   Code chunks: {stats['code_chunks']}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("UserManualChunker Demo Script")
    print("=" * 70)
    
    # Run demos
    demo_basic_usage()
    demo_with_summaries()
    demo_json_export()
    demo_directory_processing()
    demo_configuration_options()
    
    print("\n\n" + "=" * 70)
    print("All demos completed!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Markdown parsing and chunking")
    print("  ✓ Metadata extraction")
    print("  ✓ Summary generation (when configured)")
    print("  ✓ Embedding generation (when configured)")
    print("  ✓ JSON export")
    print("  ✓ Directory processing")
    print("  ✓ Configurable chunk sizes and overlap")
    print("  ✓ Statistics tracking")


if __name__ == "__main__":
    main()
