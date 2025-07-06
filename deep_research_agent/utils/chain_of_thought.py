"""
Chain-of-Thought Logging Module - Tracks agent reasoning and decision processes
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """Log levels for chain-of-thought entries"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ToolCall:
    """Structure for tool call information"""
    tool_name: str
    query: str
    parameters: Dict[str, Any]
    results: Any
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class ChainOfThoughtEntry:
    """Structure for a single chain-of-thought log entry"""
    timestamp: str
    agent: str
    step_id: str
    input_prompt: str
    tool_calls: List[ToolCall]
    llm_response: str
    decision: str
    reasoning: str
    confidence: float
    level: LogLevel
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "step_id": self.step_id,
            "input_prompt": self.input_prompt,
            "tool_calls": [asdict(tool_call) for tool_call in self.tool_calls],
            "llm_response": self.llm_response,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "level": self.level.value,
            "metadata": self.metadata
        }

class ChainOfThoughtLogger:
    """Logger for chain-of-thought processes"""
    
    def __init__(self, log_file: str = "logs/chain_of_thought.json", max_entries: int = 1000):
        """
        Initialize chain-of-thought logger
        
        Args:
            log_file: Path to log file
            max_entries: Maximum number of entries to keep in memory
        """
        self.log_file = log_file
        self.max_entries = max_entries
        self.entries: List[ChainOfThoughtEntry] = []
        self.current_session_id = self._generate_session_id()
        
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Load existing logs
        self._load_logs()
    
    def log_step(self,
                agent: str,
                input_prompt: str,
                tool_calls: List[ToolCall] = None,
                llm_response: str = "",
                decision: str = "",
                reasoning: str = "",
                confidence: float = 1.0,
                level: LogLevel = LogLevel.INFO,
                metadata: Dict[str, Any] = None) -> str:
        """
        Log a chain-of-thought step
        
        Args:
            agent: Name of the agent
            input_prompt: Input prompt given to the agent
            tool_calls: List of tool calls made
            llm_response: Response from the LLM
            decision: Decision made by the agent
            reasoning: Reasoning behind the decision
            confidence: Confidence level (0.0 to 1.0)
            level: Log level
            metadata: Additional metadata
            
        Returns:
            Step ID for reference
        """
        step_id = f"{agent}_{datetime.now().timestamp()}"
        
        entry = ChainOfThoughtEntry(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            step_id=step_id,
            input_prompt=input_prompt,
            tool_calls=tool_calls or [],
            llm_response=llm_response,
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            level=level,
            metadata={
                "session_id": self.current_session_id,
                **(metadata or {})
            }
        )
        
        self.entries.append(entry)
        
        # Trim if necessary
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        # Auto-save
        self._save_logs()
        
        return step_id
    
    def log_tool_call(self,
                     tool_name: str,
                     query: str,
                     parameters: Dict[str, Any],
                     results: Any,
                     execution_time: float,
                     success: bool,
                     error_message: Optional[str] = None) -> ToolCall:
        """
        Create a tool call log entry
        
        Args:
            tool_name: Name of the tool
            query: Query sent to the tool
            parameters: Parameters passed to the tool
            results: Results returned by the tool
            execution_time: Time taken to execute
            success: Whether the call was successful
            error_message: Error message if failed
            
        Returns:
            ToolCall object
        """
        return ToolCall(
            tool_name=tool_name,
            query=query,
            parameters=parameters,
            results=results,
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )
    
    def get_entries(self,
                   agent: Optional[str] = None,
                   level: Optional[LogLevel] = None,
                   limit: Optional[int] = None) -> List[ChainOfThoughtEntry]:
        """
        Get log entries with optional filtering
        
        Args:
            agent: Filter by agent name
            level: Filter by log level
            limit: Maximum number of entries to return
            
        Returns:
            List of filtered entries
        """
        filtered_entries = self.entries
        
        if agent:
            filtered_entries = [e for e in filtered_entries if e.agent == agent]
        
        if level:
            filtered_entries = [e for e in filtered_entries if e.level == level]
        
        if limit:
            filtered_entries = filtered_entries[-limit:]
        
        return filtered_entries
    
    def get_session_entries(self, session_id: Optional[str] = None) -> List[ChainOfThoughtEntry]:
        """Get entries for a specific session"""
        target_session = session_id or self.current_session_id
        return [e for e in self.entries if e.metadata.get("session_id") == target_session]
    
    def get_reasoning_chain(self, topic: str) -> List[ChainOfThoughtEntry]:
        """Get reasoning chain for a specific topic"""
        topic_lower = topic.lower()
        return [
            e for e in self.entries
            if topic_lower in e.input_prompt.lower() or 
               topic_lower in e.reasoning.lower() or
               topic_lower in e.decision.lower()
        ]
    
    def export_to_json(self, file_path: str, session_id: Optional[str] = None) -> None:
        """Export logs to JSON file"""
        entries_to_export = self.get_session_entries(session_id) if session_id else self.entries
        
        export_data = {
            "session_id": session_id or self.current_session_id,
            "exported_at": datetime.now().isoformat(),
            "total_entries": len(entries_to_export),
            "entries": [entry.to_dict() for entry in entries_to_export]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def create_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a summary of the reasoning process"""
        entries = self.get_session_entries(session_id) if session_id else self.entries
        
        if not entries:
            return {
                "summary": "No reasoning steps recorded",
                "total_steps": 0,
                "agents_involved": [],
                "tools_used": [],
                "average_confidence": 0.0
            }
        
        # Analyze entries
        agents_involved = list(set(e.agent for e in entries))
        tools_used = list(set(
            tool.tool_name for e in entries for tool in e.tool_calls
        ))
        
        total_confidence = sum(e.confidence for e in entries)
        average_confidence = total_confidence / len(entries)
        
        # Count by level
        level_counts = {}
        for entry in entries:
            level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
        
        # Get key decisions
        key_decisions = [
            {
                "agent": e.agent,
                "decision": e.decision,
                "confidence": e.confidence,
                "timestamp": e.timestamp
            }
            for e in entries if e.decision and e.confidence > 0.7
        ]
        
        return {
            "summary": f"Reasoning process with {len(entries)} steps across {len(agents_involved)} agents",
            "total_steps": len(entries),
            "agents_involved": agents_involved,
            "tools_used": tools_used,
            "average_confidence": round(average_confidence, 2),
            "level_distribution": level_counts,
            "key_decisions": key_decisions,
            "session_id": session_id or self.current_session_id,
            "time_span": self._calculate_time_span(entries)
        }
    
    def clear_logs(self, session_id: Optional[str] = None) -> int:
        """Clear logs, optionally for a specific session"""
        if session_id:
            original_count = len(self.entries)
            self.entries = [e for e in self.entries if e.metadata.get("session_id") != session_id]
            cleared_count = original_count - len(self.entries)
        else:
            cleared_count = len(self.entries)
            self.entries = []
        
        self._save_logs()
        return cleared_count
    
    def start_new_session(self) -> str:
        """Start a new logging session"""
        self.current_session_id = self._generate_session_id()
        return self.current_session_id
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{datetime.now().microsecond}"
    
    def _load_logs(self) -> None:
        """Load existing logs from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load entries if they exist
                if isinstance(data, dict) and "entries" in data:
                    entries_data = data["entries"]
                elif isinstance(data, list):
                    entries_data = data
                else:
                    entries_data = []
                
                # Convert to ChainOfThoughtEntry objects
                for entry_data in entries_data[-self.max_entries:]:  # Load only recent entries
                    try:
                        # Convert tool calls
                        tool_calls = []
                        for tool_data in entry_data.get("tool_calls", []):
                            tool_calls.append(ToolCall(**tool_data))
                        
                        # Create entry
                        entry = ChainOfThoughtEntry(
                            timestamp=entry_data["timestamp"],
                            agent=entry_data["agent"],
                            step_id=entry_data["step_id"],
                            input_prompt=entry_data["input_prompt"],
                            tool_calls=tool_calls,
                            llm_response=entry_data["llm_response"],
                            decision=entry_data["decision"],
                            reasoning=entry_data["reasoning"],
                            confidence=entry_data["confidence"],
                            level=LogLevel(entry_data["level"]),
                            metadata=entry_data["metadata"]
                        )
                        self.entries.append(entry)
                        
                    except Exception as e:
                        print(f"Error loading log entry: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error loading logs: {e}")
    
    def _save_logs(self) -> None:
        """Save logs to file"""
        try:
            export_data = {
                "session_id": self.current_session_id,
                "saved_at": datetime.now().isoformat(),
                "total_entries": len(self.entries),
                "entries": [entry.to_dict() for entry in self.entries]
            }
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def _calculate_time_span(self, entries: List[ChainOfThoughtEntry]) -> str:
        """Calculate time span of entries"""
        if not entries:
            return "0 seconds"
        
        try:
            first_time = datetime.fromisoformat(entries[0].timestamp)
            last_time = datetime.fromisoformat(entries[-1].timestamp)
            delta = last_time - first_time
            
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

# Global logger instance
_global_logger = None

def get_logger(log_file: str = "logs/chain_of_thought.json") -> ChainOfThoughtLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ChainOfThoughtLogger(log_file)
    return _global_logger

def log_agent_step(agent: str, **kwargs) -> str:
    """Convenience function to log an agent step"""
    logger = get_logger()
    return logger.log_step(agent=agent, **kwargs) 