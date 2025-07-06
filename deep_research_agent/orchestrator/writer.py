"""
Writer Agent - Compiles research data into structured reports
"""

from typing import Dict, List, Any
from .planner import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self):
        self.agent_name = "Writer"
        self.report_formats = ["markdown", "html", "pdf"]
    
    def execute(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile research data into a structured report
        
        Args:
            research_data: Data collected by ResearcherAgent
            
        Returns:
            Dict containing the compiled report and metadata
        """
        # Extract topic from research data if available
        topic = research_data.get("topic", "Research Topic")
        
        # Generate report sections
        report_sections = self._generate_report_sections(research_data)
        
        # Compile final report
        final_report = self._compile_report(topic, report_sections)
        
        return {
            "success": True,
            "report": final_report,
            "format": "markdown",
            "word_count": len(final_report.split()),
            "sections_count": len(report_sections),
            "reasoning": f"Compiled report with {len(report_sections)} sections"
        }
    
    def _generate_report_sections(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate report sections from research data"""
        sections = {}
        
        # TODO: Implement LLM-based content generation
        for section_name, section_data in data.items():
            if isinstance(section_data, dict) and "content" in section_data:
                sections[section_name] = self._write_section(section_name, section_data)
            else:
                # Handle simple string data
                sections[section_name] = f"## {section_name}\n\n{section_data}\n"
        
        return sections
    
    def _write_section(self, section_name: str, section_data: Dict[str, Any]) -> str:
        """Write a single section of the report"""
        # TODO: Use LLM to generate well-structured content
        content = section_data.get("content", "No content available")
        sources = section_data.get("sources", [])
        
        section_text = f"## {section_name}\n\n"
        section_text += f"{content}\n\n"
        
        if sources:
            section_text += "### Sources:\n"
            for i, source in enumerate(sources, 1):
                section_text += f"{i}. {source}\n"
            section_text += "\n"
        
        return section_text
    
    def _compile_report(self, topic: str, sections: Dict[str, str]) -> str:
        """Compile all sections into final report"""
        report = f"# Research Report: {topic}\n\n"
        report += f"*Generated on: {self._get_current_date()}*\n\n"
        
        # Add table of contents
        report += "## Table of Contents\n\n"
        for section_name in sections.keys():
            report += f"- [{section_name}](#{section_name.lower().replace(' ', '-')})\n"
        report += "\n---\n\n"
        
        # Add all sections
        for section_content in sections.values():
            report += section_content + "\n"
        
        return report
    
    def _get_current_date(self) -> str:
        """Get current date for report metadata"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_report(self, report: str) -> bool:
        """Validate the quality and completeness of the report"""
        # Basic validation checks
        if len(report) < 100:  # Too short
            return False
        if "# Research Report:" not in report:  # Missing title
            return False
        if "## " not in report:  # No sections
            return False
        return True
    
    def format_report(self, report: str, format_type: str = "markdown") -> str:
        """Format report for different output types"""
        # TODO: Implement different formatting options
        if format_type == "html":
            # Convert markdown to HTML
            return f"<html><body>{report}</body></html>"
        elif format_type == "pdf":
            # Handle PDF conversion
            return report  # Placeholder
        else:
            return report  # Default markdown 