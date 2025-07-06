"""
Agent Manager - Coordinates the flow between Planner, Researcher, and Writer agents
"""

from typing import Dict, List, Any
import json
from datetime import datetime

class AgentManager:
    def __init__(self):
        self.chain_of_thought_log = []
        self.current_topic = None
        self.research_plan = None
        self.research_data = {}
        self.final_report = None
    
    def log_step(self, agent: str, input_prompt: str, tool_calls: List[Dict], 
                 llm_response: str, decision: str):
        """Log a step in the chain of thought"""
        step = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "input_prompt": input_prompt,
            "tool_calls": tool_calls,
            "llm_response": llm_response,
            "decision": decision
        }
        self.chain_of_thought_log.append(step)
    
    def start_research(self, topic: str) -> Dict[str, Any]:
        """Main orchestration method - coordinates all agents"""
        self.current_topic = topic
        self.chain_of_thought_log = []
        
        try:
            # Step 1: Planning
            self.research_plan = self._run_planner(topic)
            
            # Step 2: Research
            self.research_data = self._run_researchers(self.research_plan)
            
            # Step 3: Writing
            self.final_report = self._run_writer(self.research_data)
            
            return {
                "success": True,
                "plan": self.research_plan,
                "data": self.research_data,
                "report": self.final_report,
                "chain_of_thought": self.chain_of_thought_log
            }
        
        except Exception as e:
            self.log_step("Manager", f"Error in research process", [], 
                         str(e), "Research failed")
            return {
                "success": False,
                "error": str(e),
                "chain_of_thought": self.chain_of_thought_log
            }
    
    def _run_planner(self, topic: str) -> Dict[str, Any]:
        """Run the planner agent"""
        # Placeholder - will be implemented when planner.py is ready
        plan = {"sections": ["Introduction", "Background", "Analysis", "Conclusion"]}
        self.log_step("Planner", f"Plan research for: {topic}", [], 
                     f"Created plan with {len(plan['sections'])} sections", 
                     "Plan approved")
        return plan
    
    def _run_researchers(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Run researcher agents for each section"""
        # Placeholder - will be implemented when researcher.py is ready
        data = {}
        for section in plan.get("sections", []):
            data[section] = f"Research data for {section}"
            self.log_step("Researcher", f"Research section: {section}", 
                         [{"tool": "web_search", "query": section, "results": ["mock result"]}], 
                         f"Found relevant information for {section}", 
                         f"Data collected for {section}")
        return data
    
    def _run_writer(self, data: Dict[str, Any]) -> str:
        """Run writer agent to compile final report"""
        # Placeholder - will be implemented when writer.py is ready
        report = f"# Research Report on {self.current_topic}\n\n"
        for section, content in data.items():
            report += f"## {section}\n{content}\n\n"
        
        self.log_step("Writer", "Compile final report", [], 
                     f"Generated report with {len(data)} sections", 
                     "Report completed")
        return report
    
    def get_chain_of_thought(self) -> List[Dict]:
        """Get the current chain of thought log"""
        return self.chain_of_thought_log
    
    def save_logs(self, filepath: str = "logs/chain_of_thought.json"):
        """Save chain of thought logs to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.chain_of_thought_log, f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}") 