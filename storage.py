import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class JSONStorage:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def save_document(self, doc_id: str, data: Dict[str, Any]):
        file_path = os.path.join(self.data_dir, f"document_{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        file_path = os.path.join(self.data_dir, f"document_{doc_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def save_segments(self, doc_id: str, segments: List[Dict[str, Any]]):
        file_path = os.path.join(self.data_dir, f"segments_{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2, default=str)
    
    def load_segments(self, doc_id: str) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.data_dir, f"segments_{doc_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def save_knowledge_graph(self, graph_data: Dict[str, Any]):
        file_path = os.path.join(self.data_dir, "knowledge_graph.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_knowledge_graph(self) -> Dict[str, Any]:
        file_path = os.path.join(self.data_dir, "knowledge_graph.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"nodes": [], "edges": []}
    
    def save_vectors(self, vectors_data: Dict[str, Any]):
        file_path = os.path.join(self.data_dir, "vectors.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(vectors_data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_vectors(self) -> Dict[str, Any]:
        file_path = os.path.join(self.data_dir, "vectors.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def list_documents(self) -> List[str]:
        files = [f for f in os.listdir(self.data_dir) if f.startswith("document_") and f.endswith(".json")]
        return [f.replace("document_", "").replace(".json", "") for f in files]

storage = JSONStorage()