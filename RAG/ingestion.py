from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
import os

def load_pdf(file_path: str) -> str:
    logger.info(f"Loading PDF: {file_path}")
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    logger.info(f"Extracted {len(text)} characters from PDF")
    return text

def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext in [".txt", ".md", ".py"]:
        return load_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_text(text)
    logger.info(f"Created {len(chunks)} chunks")
    return chunks

def ingest_file(file_path: str) -> list[str]:
    text = load_document(file_path)
    chunks = chunk_text(text)
    return chunks