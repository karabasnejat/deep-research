"""
Agent Manager - Coordinates the flow between Planner, Researcher, and Writer agents
"""

from typing import Dict, List, Any
import json
from datetime import datetime
import time

# Import the new chain-of-thought logging system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.chain_of_thought import ChainOfThoughtLogger, LogLevel, ToolCall

class AgentManager:
    def __init__(self):
        self.cot_logger = ChainOfThoughtLogger()
        self.current_topic = None
        self.research_plan = None
        self.research_data = {}
        self.final_report = None
        self.session_id = self.cot_logger.start_new_session()
    
    def start_research(self, topic: str) -> Dict[str, Any]:
        """Main orchestration method - coordinates all agents"""
        self.current_topic = topic
        
        # Log the start of research
        self.cot_logger.log_step(
            agent="Manager",
            input_prompt=f"Starting research on topic: {topic}",
            reasoning="Initiating research workflow with topic analysis",
            decision="Begin with planning phase",
            confidence=1.0,
            level=LogLevel.INFO
        )
        
        try:
            # Step 1: Planning
            self.research_plan = self._run_planner(topic)
            
            # Step 2: Research
            self.research_data = self._run_researchers(self.research_plan)
            
            # Step 3: Writing
            self.final_report = self._run_writer(self.research_data)
            
            # Log successful completion
            self.cot_logger.log_step(
                agent="Manager",
                input_prompt="Research workflow completed",
                reasoning="All phases completed successfully",
                decision="Return results to user",
                confidence=1.0,
                level=LogLevel.INFO,
                metadata={"topic": topic, "success": True}
            )
            
            return {
                "success": True,
                "plan": self.research_plan,
                "data": self.research_data,
                "report": self.final_report,
                "chain_of_thought": self.get_chain_of_thought_summary(),
                "session_id": self.session_id
            }
        
        except Exception as e:
            # Log error
            self.cot_logger.log_step(
                agent="Manager",
                input_prompt=f"Error in research process: {str(e)}",
                reasoning="Exception occurred during research workflow",
                decision="Abort research and return error",
                confidence=0.0,
                level=LogLevel.ERROR,
                metadata={"error": str(e), "topic": topic}
            )
            
            return {
                "success": False,
                "error": str(e),
                "chain_of_thought": self.get_chain_of_thought_summary(),
                "session_id": self.session_id
            }
    
    def _run_planner(self, topic: str) -> Dict[str, Any]:
        """Run the planner agent with detailed logging"""
        start_time = time.time()
        
        # Log planner start
        step_id = self.cot_logger.log_step(
            agent="Planner",
            input_prompt=f"Plan research for topic: {topic}",
            reasoning="Analyzing topic to create structured research plan",
            decision="Generate research sections and approaches",
            confidence=0.9,
            level=LogLevel.INFO
        )
        
        try:
            # Placeholder - will be implemented when planner.py is ready
            plan = {
                "sections": ["Introduction", "Background", "Current State", "Analysis", "Conclusion"],
                "research_approaches": ["web_search", "academic_search"],
                "estimated_time": "30 minutes"
            }
            
            execution_time = time.time() - start_time
            
            # Log successful planning
            self.cot_logger.log_step(
                agent="Planner",
                input_prompt=f"Planning completed for: {topic}",
                reasoning=f"Generated {len(plan['sections'])} research sections with multiple approaches",
                decision="Plan approved and ready for research phase",
                confidence=0.95,
                level=LogLevel.INFO,
                metadata={
                    "execution_time": execution_time,
                    "sections_count": len(plan['sections']),
                    "approaches": plan['research_approaches']
                }
            )
            
            return plan
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log planning error
            self.cot_logger.log_step(
                agent="Planner",
                input_prompt=f"Planning failed for: {topic}",
                reasoning=f"Error during planning: {str(e)}",
                decision="Use fallback planning approach",
                confidence=0.3,
                level=LogLevel.ERROR,
                metadata={"error": str(e), "execution_time": execution_time}
            )
            
            # Return fallback plan
            return {
                "sections": ["Overview", "Analysis", "Conclusion"],
                "research_approaches": ["web_search"],
                "estimated_time": "20 minutes"
            }
    
    def _run_researchers(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Run researcher agents for each section with detailed logging"""
        data = {}
        
        for section in plan.get("sections", []):
            start_time = time.time()
            
            # Log research start for section
            self.cot_logger.log_step(
                agent="Researcher",
                input_prompt=f"Research section: {section}",
                reasoning=f"Gathering information for {section} using available tools",
                decision="Execute search queries and collect data",
                confidence=0.8,
                level=LogLevel.INFO
            )
            
            try:
                # Simulate tool calls
                tool_calls = []
                
                # Simulate web search
                web_start = time.time()
                web_results = f"Web search results for {section}"
                web_tool_call = ToolCall(
                    tool_name="web_search",
                    query=f"{section} {self.current_topic}",
                    parameters={"num_results": 10},
                    results=web_results,
                    execution_time=time.time() - web_start,
                    success=True
                )
                tool_calls.append(web_tool_call)
                
                # Simulate academic search
                acad_start = time.time()
                acad_results = f"Academic search results for {section}"
                acad_tool_call = ToolCall(
                    tool_name="academic_search",
                    query=f"{section} {self.current_topic}",
                    parameters={"max_results": 5},
                    results=acad_results,
                    execution_time=time.time() - acad_start,
                    success=True
                )
                tool_calls.append(acad_tool_call)
                
                # Compile section data
                section_data = {
                    "content": f"Research content for {section}",
                    "sources": ["web_source_1", "academic_source_1"],
                    "confidence": 0.85
                }
                data[section] = section_data
                
                execution_time = time.time() - start_time
                
                # Log successful research
                self.cot_logger.log_step(
                    agent="Researcher",
                    input_prompt=f"Research completed for: {section}",
                    tool_calls=tool_calls,
                    reasoning=f"Successfully collected data from {len(tool_calls)} sources",
                    decision=f"Data quality sufficient for {section}",
                    confidence=0.85,
                    level=LogLevel.INFO,
                    metadata={
                        "execution_time": execution_time,
                        "sources_count": len(section_data["sources"]),
                        "section": section
                    }
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log research error
                self.cot_logger.log_step(
                    agent="Researcher",
                    input_prompt=f"Research failed for: {section}",
                    reasoning=f"Error during research: {str(e)}",
                    decision="Use fallback content for section",
                    confidence=0.3,
                    level=LogLevel.ERROR,
                    metadata={"error": str(e), "execution_time": execution_time, "section": section}
                )
                
                # Fallback data
                data[section] = {
                    "content": f"Fallback content for {section}",
                    "sources": [],
                    "confidence": 0.3
                }
        
        return data
    
    def _run_writer(self, data: Dict[str, Any]) -> str:
        """Run writer agent to compile final report with detailed logging"""
        start_time = time.time()
        
        # Log writer start
        self.cot_logger.log_step(
            agent="Writer",
            input_prompt="Compile final report from research data",
            reasoning=f"Structuring report from {len(data)} research sections",
            decision="Generate comprehensive markdown report",
            confidence=0.9,
            level=LogLevel.INFO
        )
        
        try:
            # Generate report
            report = f"# Research Report: {self.current_topic}\n\n"
            report += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            
            for section, content in data.items():
                report += f"## {section}\n\n"
                report += f"{content.get('content', 'No content available')}\n\n"
                
                if content.get('sources'):
                    report += "### Sources:\n"
                    for i, source in enumerate(content['sources'], 1):
                        report += f"{i}. {source}\n"
                    report += "\n"
            
            execution_time = time.time() - start_time
            
            # Log successful writing
            self.cot_logger.log_step(
                agent="Writer",
                input_prompt="Report compilation completed",
                reasoning=f"Generated {len(report.split())} word report with {len(data)} sections",
                decision="Report quality meets standards",
                confidence=0.95,
                level=LogLevel.INFO,
                metadata={
                    "execution_time": execution_time,
                    "word_count": len(report.split()),
                    "sections_count": len(data)
                }
            )
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log writing error
            self.cot_logger.log_step(
                agent="Writer",
                input_prompt="Report compilation failed",
                reasoning=f"Error during writing: {str(e)}",
                decision="Generate minimal fallback report",
                confidence=0.2,
                level=LogLevel.ERROR,
                metadata={"error": str(e), "execution_time": execution_time}
            )
            
            # Fallback report
            return f"# Research Report: {self.current_topic}\n\nError generating full report: {str(e)}"
    
    def get_chain_of_thought_summary(self) -> Dict[str, Any]:
        """Get a summary of the chain of thought for this session"""
        return self.cot_logger.create_summary(self.session_id)
    
    def get_detailed_logs(self) -> List[Dict[str, Any]]:
        """Get detailed logs for this session"""
        entries = self.cot_logger.get_session_entries(self.session_id)
        return [entry.to_dict() for entry in entries]
    
    def export_session_logs(self, file_path: str) -> None:
        """Export session logs to file"""
        self.cot_logger.export_to_json(file_path, self.session_id)
    
    def save_logs(self, filepath: str = "logs/chain_of_thought.json"):
        """Save chain of thought logs to file"""
        try:
            self.cot_logger.export_to_json(filepath, self.session_id)
        except Exception as e:
            print(f"Error saving logs: {e}") 