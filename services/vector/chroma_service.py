import asyncio
import chromadb
from config import settings
from core.models import SearchResult
from core.logging import get_logger

logger = get_logger(__name__)

class ChromaService:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=settings.chromadb_path)
            self.collection = self.client.get_or_create_collection(
                name="campus_notes",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    async def upsert_notes(self, notes: list[dict]):
        """
        Upsert a list of notes into ChromaDB.
        Runs synchronously in a thread pool since ChromaDB is sync.
        """
        if not notes:
            return

        def _upsert():
            ids = []
            documents = []
            metadatas = []
            
            for note in notes:
                ids.append(str(note.get("id")))
                documents.append(note.get("raw_text", ""))
                metadatas.append({
                    "title": note.get("title", ""),
                    "created_at": note.get("created_at", ""),
                    "is_synced": 1
                })
                
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _upsert)
            logger.info(f"Upserted {len(notes)} notes into ChromaDB")
        except Exception as e:
            logger.error(f"ChromaDB upsert failed: {e}")
            raise

    async def upsert_note(self, note_id: str, text: str, metadata: dict):
        """
        Upsert a single note.
        """
        await self.upsert_notes([{"id": note_id, "raw_text": text, **metadata}])

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Search for notes matching the query.
        """
        def _search():
            return self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, _search)
            
            search_results = []
            if results and results["ids"] and len(results["ids"]) > 0:
                ids = results["ids"][0]
                distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(ids)
                documents = results["documents"][0] if "documents" in results and results["documents"] else [""] * len(ids)
                metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(ids)
                
                for i in range(len(ids)):
                    dist = float(distances[i])
                    # Filter: distance < 0.8
                    if dist < 0.8:
                        search_results.append(SearchResult(
                            id=ids[i],
                            text=documents[i],
                            distance=dist,
                            metadata=metadatas[i]
                        ))
            
            return search_results
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

chroma_service = ChromaService()
