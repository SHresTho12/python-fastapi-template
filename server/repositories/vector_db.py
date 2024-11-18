from connection.chroma_conn import init_chroma


class ChromaDB:
    def __init__(self):
        self.chroma_db = init_chroma()

    def get_vector(self, text: str):
        return self.chroma_db.get_vector(text)

    def delete(self, ids):
        return self.chroma_db.delete(ids=ids)

    def reset_chroma(self,ids):
        self.chroma_db.delete(ids)
    def delete_collection(self):
        return self.chroma_db.delete_collection()
    def get(self, include=None):
        return self.chroma_db.get(include=include)
    
    def get_collection_list(self):
        return self.chroma_db.get()

    def add_documents(self, documents, ids=None):
        return self.chroma_db.add_documents(documents, ids=ids)

    def get_collection(self):
        return self.chroma_db._collection.get(include=["documents", "metadatas"])