from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(
    documents: List[Document], 
    collection_name: str,
    chunk_size: int = 500, 
    chunk_overlap: int = 50
) -> List[Document]:
    """Splits documents into dense chunks enriched with structural metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "### ", "## ", "# ", ". ", " "]
    )
    
    chunks = []
    for doc in documents:
        split_chunks = splitter.split_documents([doc])
        for idx, chunk in enumerate(split_chunks):
            chunk.metadata.update({
                "collection": collection_name,
                "chunk_id": f"{collection_name}_{idx}",
            })
            chunks.append(chunk)
            
    return chunks
