# ============================================
# PDF Processing Service
# ============================================
# This module handles reading PDFs and splitting them into chunks.
#
# Why split into chunks?
# - PDFs can be very long (many pages)
# - When searching, we want to find the SPECIFIC paragraph that answers a question
# - Smaller chunks = more precise answers
# - Each chunk becomes a searchable unit in our vector database
#
# Example:
# A 10-page PDF → split into 20 chunks of ~500 characters each
# User asks "refund policy?" → We find the specific chunk about refunds

import os
from typing import List, Dict
from pypdf import PdfReader
from app.config import DOCS_DIRECTORY, CHUNK_SIZE, CHUNK_OVERLAP


# ============================================
# Data Structure for Document Chunks
# ============================================
# Each chunk contains:
# - text: The actual text content
# - metadata: Information about where it came from (source, page, etc.)


def load_pdf(file_path: str) -> str:
    """
    Read all text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        All text content from the PDF as a single string
    
    Example:
        >>> text = load_pdf("data/docs/Refund_Policy.pdf")
        >>> print(text[:100])  # First 100 characters
    """
    reader = PdfReader(file_path)
    
    # Extract text from each page and combine
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    return text


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split a long text into smaller chunks with overlap.
    
    Why overlap?
    If a sentence is split between two chunks, the overlap ensures
    that important context isn't lost at the boundary.
    
    Args:
        text: The full text to split
        chunk_size: Maximum characters per chunk (default: 500)
        chunk_overlap: Characters to overlap between chunks (default: 50)
    
    Returns:
        List of text chunks
    
    Example:
        Text: "ABCDEFGHIJ" with chunk_size=5, overlap=2
        Chunks: ["ABCDE", "DEFGH", "GHIJ"]
                       ^^overlap ^^overlap
    """
    # Clean the text (remove extra whitespace)
    text = " ".join(text.split())
    
    # If text is shorter than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get the chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at a sentence or word boundary (cleaner chunks)
        if end < len(text):
            # Look for last period, question mark, or exclamation
            last_sentence = max(
                chunk.rfind(". "),
                chunk.rfind("? "),
                chunk.rfind("! ")
            )
            
            # If found a sentence break, use it
            if last_sentence > chunk_size // 2:
                chunk = text[start:start + last_sentence + 1]
                end = start + last_sentence + 1
        
        chunks.append(chunk.strip())
        
        # Move start position, accounting for overlap
        start = end - chunk_overlap
    
    return chunks


def process_pdf(file_path: str) -> List[Dict]:
    """
    Process a single PDF: read it and split into chunks with metadata.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        List of dictionaries, each containing:
        - text: The chunk text
        - metadata: Source file, chunk index, etc.
    
    Example:
        >>> chunks = process_pdf("data/docs/Refund_Policy.pdf")
        >>> print(chunks[0])
        {'text': '...', 'metadata': {'source': 'Refund_Policy.pdf', ...}}
    """
    # Get just the filename for metadata
    filename = os.path.basename(file_path)
    
    print(f"Processing: {filename}")
    
    # Load the PDF text
    text = load_pdf(file_path)
    
    if not text.strip():
        print(f"  Warning: No text extracted from {filename}")
        return []
    
    # Split into chunks
    text_chunks = split_text_into_chunks(text)
    
    # Create result with metadata for each chunk
    result = []
    for i, chunk_text in enumerate(text_chunks):
        result.append({
            "text": chunk_text,
            "metadata": {
                "source": filename,          # Which PDF this came from
                "chunk_index": i,            # Which chunk number (0, 1, 2, ...)
                "total_chunks": len(text_chunks),  # Total chunks in this PDF
            }
        })
    
    print(f"  Created {len(result)} chunks")
    return result


def process_all_pdfs(directory: str = DOCS_DIRECTORY) -> List[Dict]:
    """
    Process all PDF files in a directory.
    
    Args:
        directory: Path to folder containing PDFs (default: data/docs)
    
    Returns:
        List of all chunks from all PDFs
    """
    all_chunks = []
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found!")
        return []
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return []
    
    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 50)
    
    # Process each PDF
    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)
        chunks = process_pdf(file_path)
        all_chunks.extend(chunks)
    
    print("=" * 50)
    print(f"Total chunks created: {len(all_chunks)}")
    
    return all_chunks


# ============================================
# Test the PDF processing service
# ============================================
if __name__ == "__main__":
    print("Testing PDF Processing Service")
    print("=" * 50)
    
    # Process all PDFs
    chunks = process_all_pdfs()
    
    if chunks:
        # Show sample of first chunk
        print("\n" + "=" * 50)
        print("Sample chunk (first one):")
        print("-" * 50)
        sample = chunks[0]
        print(f"Source: {sample['metadata']['source']}")
        print(f"Chunk: {sample['metadata']['chunk_index'] + 1} of {sample['metadata']['total_chunks']}")
        print(f"Text preview: {sample['text'][:200]}...")
        
        print("\n✅ PDF processing service is working correctly!")
