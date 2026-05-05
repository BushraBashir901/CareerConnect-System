"""Memory manager service for conversation history."""

from typing import Dict, Any, List


class MemoryManager:
    """Simple memory manager for conversation history."""
    
    def __init__(self):
        """Initialize the memory manager."""
        self.messages: List[Dict[str, Any]] = []
    
    async def add_message(self, message, store_in_long_term: bool = False):
        """Add a message to memory."""
        # Simple implementation - in a real system this would store to database
        self.messages.append({
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.timestamp,
            "session_id": message.session_id
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_messages": len(self.messages),
            "sessions": len(set(msg.get("session_id") for msg in self.messages))
        }
