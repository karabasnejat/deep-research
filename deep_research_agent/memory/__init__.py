"""
Memory package for Deep Research Agent
Contains short-term and long-term memory modules
"""

from .short_term import ShortTermMemory
from .long_term import LongTermMemory

__all__ = [
    'ShortTermMemory',
    'LongTermMemory'
]

# Memory factory functions
def create_short_term_memory(max_messages: int = 20, max_age_hours: int = 24):
    """Create a short-term memory instance"""
    return ShortTermMemory(max_messages=max_messages, max_age_hours=max_age_hours)

def create_long_term_memory(vector_store_type: str = "chroma", 
                           collection_name: str = "research_memory",
                           persist_directory: str = "./memory_db"):
    """Create a long-term memory instance"""
    return LongTermMemory(
        vector_store_type=vector_store_type,
        collection_name=collection_name,
        persist_directory=persist_directory
    )

class MemoryManager:
    """Unified memory manager for both short-term and long-term memory"""
    
    def __init__(self, 
                 short_term_config: dict = None,
                 long_term_config: dict = None):
        """
        Initialize memory manager
        
        Args:
            short_term_config: Configuration for short-term memory
            long_term_config: Configuration for long-term memory
        """
        # Initialize short-term memory
        st_config = short_term_config or {}
        self.short_term = create_short_term_memory(**st_config)
        
        # Initialize long-term memory
        lt_config = long_term_config or {}
        self.long_term = create_long_term_memory(**lt_config)
    
    def add_conversation_message(self, message: dict):
        """Add a message to short-term memory"""
        self.short_term.add_message(message)
    
    def store_important_memory(self, content: str, metadata: dict = None, importance: float = 1.0):
        """Store important information in long-term memory"""
        return self.long_term.store_memory(content, metadata, importance=importance)
    
    def get_relevant_context(self, query: str, include_short_term: bool = True, include_long_term: bool = True):
        """Get relevant context from both memory types"""
        context = {
            "short_term": [],
            "long_term": []
        }
        
        if include_short_term:
            context["short_term"] = self.short_term.search_messages(query)
        
        if include_long_term:
            context["long_term"] = self.long_term.retrieve_memories(query)
        
        return context
    
    def get_memory_summary(self):
        """Get summary of both memory types"""
        return {
            "short_term": self.short_term.summarize_conversation(),
            "long_term": self.long_term.get_memory_stats()
        } 