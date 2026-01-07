import json
import os
from pathlib import Path
from typing import List, Dict, Optional

from app.core.config import settings


class EmbeddingsStorage:
    """
    Local file-based storage for face embeddings.
    Each student has a JSON file: {student_id}.json
    """
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Failed to create storage directory {storage_path}: {e}")
    
    def _get_file_path(self, student_id: str) -> Path:
        """Get the file path for a student's embeddings."""
        return self.storage_path / f"{student_id}.json"
    
    def save_embedding(self, student_id: str, embedding: List[float]) -> None:
        """
        Save a face embedding for a student.
        Multiple embeddings can be stored per student (different angles, lighting).
        
        Args:
            student_id: Unique student identifier
            embedding: 128-dimensional face embedding
        """
        if not student_id or not student_id.strip():
            raise ValueError("student_id cannot be empty")
        
        file_path = self._get_file_path(student_id)
        
        # Load existing embeddings or create new list
        embeddings = []
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    embeddings = json.load(f)
            except (json.JSONDecodeError, IOError):
                embeddings = []
        
        # Append new embedding
        embeddings.append(embedding)
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(embeddings, f, indent=2)
    
    def get_embeddings(self, student_id: str) -> Optional[List[List[float]]]:
        """
        Get all embeddings for a student.
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            List of embeddings or None if student not found
        """
        if not student_id or not student_id.strip():
            return None
        
        file_path = self._get_file_path(student_id)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def delete_embeddings(self, student_id: str) -> bool:
        """
        Delete all embeddings for a student.
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            True if deleted, False if not found
        """
        if not student_id or not student_id.strip():
            return False
        
        file_path = self._get_file_path(student_id)
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_all_student_embeddings(self) -> Dict[str, List[List[float]]]:
        """
        Get embeddings for all students.
        
        Returns:
            Dictionary mapping student_id to list of embeddings
        """
        all_embeddings = {}
        
        for file_path in self.storage_path.glob("*.json"):
            student_id = file_path.stem
            try:
                with open(file_path, 'r') as f:
                    embeddings = json.load(f)
                    if embeddings:  # Only include if has embeddings
                        all_embeddings[student_id] = embeddings
            except (json.JSONDecodeError, IOError):
                continue
        
        return all_embeddings
    
    def student_has_embeddings(self, student_id: str) -> bool:
        """
        Check if a student has any embeddings stored.
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            True if student has embeddings, False otherwise
        """
        if not student_id or not student_id.strip():
            return False
        
        embeddings = self.get_embeddings(student_id)
        return embeddings is not None and len(embeddings) > 0

# Global instance - initialized once at module load
# For testing, you can mock this or create a new instance
embeddings_storage = EmbeddingsStorage(settings.EMBEDDINGS_STORAGE_PATH)
