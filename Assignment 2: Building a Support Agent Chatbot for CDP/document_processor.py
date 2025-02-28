import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

class DocumentProcessor:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
    def process_directory(self, directory_path, cdp_name):
        """Process all text files in a directory and create documents with metadata."""
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        
        documents = loader.load()
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata["cdp"] = cdp_name
            doc.metadata["source"] = os.path.basename(doc.metadata["source"])
            
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        print(f"Processed {len(documents)} documents into {len(chunks)} chunks for {cdp_name}")
        
        return chunks
    
    def create_vector_database(self, all_chunks):
        """Create a vector database from document chunks."""
        vector_db = FAISS.from_documents(all_chunks, self.embeddings)
        return vector_db
    
    def save_vector_database(self, vector_db, save_path="vectorstore"):
        """Save the vector database to disk."""
        vector_db.save_local(save_path)
        print(f"Vector database saved to {save_path}")
        
    def load_vector_database(self, load_path="vectorstore"):
        """Load the vector database from disk."""
        vector_db = FAISS.load_local(load_path, self.embeddings)
        return vector_db

# Usage example
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Process each CDP's documentation
    segment_chunks = processor.process_directory("segment_docs", "segment")
    mparticle_chunks = processor.process_directory("mparticle_docs", "mparticle")
    lytics_chunks = processor.process_directory("lytics_docs", "lytics")
    zeotap_chunks = processor.process_directory("zeotap_docs", "zeotap")
    
    # Combine all chunks
    all_chunks = segment_chunks + mparticle_chunks + lytics_chunks + zeotap_chunks
    
    # Create and save vector database
    vector_db = processor.create_vector_database(all_chunks)
    processor.save_vector_database(vector_db)
