from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

from ..models.content import ContentHistory, Content

class HistoryService:
    def __init__(self):
        self.history_file = "storage/history.json"
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as f:
                json.dump([], f)

    async def get_history(self, skip: int = 0, limit: int = 10) -> List[ContentHistory]:
        """
        Retrieve paginated content history.
        """
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            
            # Sort by created_at in descending order
            history.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            return history[skip:skip + limit]
        except Exception as e:
            print(f"Error retrieving history: {str(e)}")
            return []

    async def add_to_history(self, content: Content, topic: str, content_type: str) -> str:
        """
        Add content to history.
        """
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            
            content_id = str(uuid.uuid4())
            history_entry = {
                "id": content_id,
                "topic": topic,
                "content_type": content_type,
                "created_at": datetime.utcnow().isoformat(),
                "content": content.dict()
            }
            
            history.append(history_entry)
            
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
            
            return content_id
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            return None

    async def delete_content(self, content_id: str) -> bool:
        """
        Delete content from history.
        """
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            
            # Filter out the content to delete
            history = [entry for entry in history if entry["id"] != content_id]
            
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting content: {str(e)}")
            return False 