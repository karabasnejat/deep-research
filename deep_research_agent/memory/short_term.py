"""
Short-term Memory Module - Manages conversation buffer and recent interactions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class ShortTermMemory:
    def __init__(self, max_messages: int = 20, max_age_hours: int = 24):
        """
        Initialize short-term memory
        
        Args:
            max_messages: Maximum number of messages to keep in buffer
            max_age_hours: Maximum age of messages in hours before auto-cleanup
        """
        self.max_messages = max_messages
        self.max_age_hours = max_age_hours
        self.messages = []
        self.session_id = None
        self.created_at = datetime.now()
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to short-term memory
        
        Args:
            message: Message dict with required fields: role, content, timestamp
        """
        # Ensure required fields
        if not all(key in message for key in ['role', 'content']):
            raise ValueError("Message must contain 'role' and 'content' fields")
        
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        # Add message ID if not present
        if 'id' not in message:
            message['id'] = f"msg_{len(self.messages)}_{datetime.now().timestamp()}"
        
        self.messages.append(message)
        
        # Auto-trim if necessary
        self._auto_trim()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from short-term memory
        
        Args:
            limit: Maximum number of recent messages to return
            
        Returns:
            List of message dictionaries
        """
        # Clean up old messages first
        self._cleanup_old_messages()
        
        if limit is None:
            return self.messages.copy()
        
        return self.messages[-limit:] if limit > 0 else []
    
    def get_conversation_context(self) -> str:
        """
        Get conversation context as formatted string
        
        Returns:
            Formatted conversation context
        """
        context_parts = []
        
        for msg in self.messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            context_parts.append(f"[{role.upper()}] {content}")
        
        return "\n".join(context_parts)
    
    def summarize_conversation(self) -> Dict[str, Any]:
        """
        Create a summary of the conversation
        
        Returns:
            Summary dictionary with key topics and statistics
        """
        if not self.messages:
            return {
                "summary": "No conversation history",
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "key_topics": [],
                "time_span": "0 minutes"
            }
        
        # Count message types
        user_messages = len([m for m in self.messages if m.get('role') == 'user'])
        assistant_messages = len([m for m in self.messages if m.get('role') == 'assistant'])
        system_messages = len([m for m in self.messages if m.get('role') == 'system'])
        
        # Calculate time span
        first_msg_time = self._parse_timestamp(self.messages[0].get('timestamp'))
        last_msg_time = self._parse_timestamp(self.messages[-1].get('timestamp'))
        time_span = self._calculate_time_span(first_msg_time, last_msg_time)
        
        # Extract key topics (simple keyword extraction)
        key_topics = self._extract_key_topics()
        
        # Create summary text
        summary_text = self._generate_summary_text()
        
        return {
            "summary": summary_text,
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": system_messages,
            "key_topics": key_topics,
            "time_span": time_span,
            "created_at": self.created_at.isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def clear_memory(self) -> None:
        """Clear all messages from short-term memory"""
        self.messages = []
    
    def trim_to_limit(self, new_limit: int) -> List[Dict[str, Any]]:
        """
        Trim messages to a new limit and return removed messages
        
        Args:
            new_limit: New message limit
            
        Returns:
            List of removed messages
        """
        if new_limit >= len(self.messages):
            return []
        
        removed_messages = self.messages[:-new_limit]
        self.messages = self.messages[-new_limit:]
        
        return removed_messages
    
    def search_messages(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for messages containing specific text
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        query_lower = query.lower()
        matching_messages = []
        
        for msg in self.messages:
            content = msg.get('content', '').lower()
            if query_lower in content:
                matching_messages.append(msg)
        
        return matching_messages[-limit:] if limit > 0 else matching_messages
    
    def _auto_trim(self) -> None:
        """Automatically trim messages if over limit"""
        if len(self.messages) > self.max_messages:
            # Keep the most recent messages
            self.messages = self.messages[-self.max_messages:]
    
    def _cleanup_old_messages(self) -> None:
        """Remove messages older than max_age_hours"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        
        self.messages = [
            msg for msg in self.messages
            if self._parse_timestamp(msg.get('timestamp')) > cutoff_time
        ]
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return datetime.now()
        except (ValueError, TypeError):
            return datetime.now()
    
    def _calculate_time_span(self, start_time: datetime, end_time: datetime) -> str:
        """Calculate human-readable time span"""
        try:
            delta = end_time - start_time
            
            if delta.days > 0:
                return f"{delta.days} days"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hours"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} minutes"
            else:
                return f"{delta.seconds} seconds"
        except:
            return "unknown"
    
    def _extract_key_topics(self) -> List[str]:
        """Extract key topics from conversation (simple keyword extraction)"""
        # TODO: Implement more sophisticated topic extraction using NLP
        all_text = " ".join([msg.get('content', '') for msg in self.messages])
        
        # Simple keyword extraction
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        words = all_text.lower().split()
        word_freq = {}
        
        for word in words:
            word = word.strip('.,!?;:"()[]{}')
            if len(word) > 3 and word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 5 most frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [word for word, freq in top_words]
    
    def _generate_summary_text(self) -> str:
        """Generate a text summary of the conversation"""
        if not self.messages:
            return "No conversation history available."
        
        user_messages = [m for m in self.messages if m.get('role') == 'user']
        assistant_messages = [m for m in self.messages if m.get('role') == 'assistant']
        
        if not user_messages:
            return "Conversation contains only system messages."
        
        # Get first and last user messages for context
        first_user_msg = user_messages[0].get('content', '')[:100] + "..."
        last_user_msg = user_messages[-1].get('content', '')[:100] + "..."
        
        summary = f"Conversation started with: {first_user_msg}"
        if len(user_messages) > 1:
            summary += f" Most recent topic: {last_user_msg}"
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Export memory state to dictionary"""
        return {
            "messages": self.messages,
            "max_messages": self.max_messages,
            "max_age_hours": self.max_age_hours,
            "created_at": self.created_at.isoformat(),
            "session_id": self.session_id
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Import memory state from dictionary"""
        self.messages = data.get("messages", [])
        self.max_messages = data.get("max_messages", 20)
        self.max_age_hours = data.get("max_age_hours", 24)
        self.session_id = data.get("session_id")
        
        created_at_str = data.get("created_at")
        if created_at_str:
            self.created_at = self._parse_timestamp(created_at_str) 