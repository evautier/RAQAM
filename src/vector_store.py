import os
import numpy as np

import faiss
from langchain.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

import concurrent.futures

from tqdm import tqdm


class VectorStore():
    def __init__(self,
                 embedding_model,
                 embedding_batch_size,
                 local_vector_store_path=None):
        """
        FAISS Vectors Store with specific embeddings model

        @param embedding_model: Model for embeddings to use for this vector store 
        @param embedding_batch_size: Size of batch for which to calculate embeddings      
        @param local_vector_store_path: Path to use to load vector store
        """
        self.embedding_model = embedding_model
        self.embedding_batch_size = embedding_batch_size
        if local_vector_store_path is None or not os.path.exists(local_vector_store_path):
            # Creating index with faiss
            index = faiss.IndexFlatL2(len(self.embedding_model.embed_query("hello world")))
            # Creating vector store with corresponding embedding function and index
            self.vector_store = FAISS(
                embedding_function=self.embedding_model,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            ) 
        else:
            self.vector_store = FAISS.load_local(local_vector_store_path, self.embedding_model, allow_dangerous_deserialization=True)
    
    def generate_embeddings(self,
                            chunks):
        """
        Generates text embeddings for chunks by batch and with parallelization

        @param chunks: Text chunks for which to generate embeddings
        """
        embeddings = []
        # Split chunks into batches for parallel processing
        batches = [chunks[i:i + self.embedding_batch_size] for i in range(0, len(chunks), self.embedding_batch_size)]        
        # Create a tqdm progress bar for monitoring
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use tqdm to wrap the list of batches being processed
            batch_embeddings = list(tqdm(executor.map(self.embedding_model.embed_documents, batches), total=len(batches), desc="Generating embeddings"))        
        # Flatten the list of batches
        for batch in batch_embeddings:
            embeddings.extend(batch)
        return np.array(embeddings)

    def add_embedded_chunks(self,
                            chunks):
        """
        Creates the vector stores with corresponding embeddings model and loads the text chunks

        @param chunks: Text chunks for which to generate embeddings and to store in vector store
        """
        # Generating embeddings 
        embeddings = self.generate_embeddings(chunks)
        self.vector_store.add_embeddings(text_embeddings=zip(chunks, embeddings))

    def find_relevant_chunks(self,
                             query,
                             k=5):
        """
        Retrieves relevant content chunks from vector store using a specific query. 

        @param query: Query to use to retrieve document
        @param k: Number of results to retrieve from query        
        """
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def save_vector_store(self,
                          path):
        """
        Saves the generated vector store to a local file

        @param: Path where to save local vector store        
        """
        self.vector_store.save_local(path)