import chromadb
from chromadb.config import Settings
from config import Config

class CollectionsService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

    def create_collection(self, name: str):
        self.chroma_client.get_or_create_collection(name=name)

    def delete_collection(self, name: str):
        self.chroma_client.delete_collection(name=name)

    def list_collections(self):
        return [col.name for col in self.chroma_client.list_collections()] 