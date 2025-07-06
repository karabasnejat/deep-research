"""
Prompt Templates Module - Contains structured prompts for different agents and research phases
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    """Types of prompts available"""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYZER = "analyzer"
    SUMMARIZER = "summarizer"

@dataclass
class PromptTemplate:
    """Structure for prompt templates"""
    name: str
    type: PromptType
    template: str
    variables: List[str]
    description: str
    example_input: Dict[str, Any]
    expected_output: str

class PromptManager:
    """Manager for prompt templates and generation"""
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize default prompt templates"""
        
        # Planner Agent Prompts
        self.templates["research_planner"] = PromptTemplate(
            name="research_planner",
            type=PromptType.PLANNER,
            template="""You are a Research Planning Agent. Your task is to analyze a research topic and create a comprehensive research plan.

TOPIC: {topic}

CONTEXT:
- Research depth: {depth}
- Available sources: {sources}
- Time constraint: {time_limit}
- Target audience: {audience}

INSTRUCTIONS:
1. Analyze the topic to understand its scope and complexity
2. Identify key research areas and subtopics
3. Determine the most effective research approaches
4. Create a logical sequence of research sections
5. Estimate time and resources needed

OUTPUT FORMAT:
Provide a JSON response with:
- "sections": List of research sections in logical order
- "research_approaches": List of recommended research methods
- "estimated_time": Time estimate in minutes
- "priority_sources": Ordered list of source types by importance
- "key_questions": Important questions to address
- "reasoning": Explanation of your planning decisions

EXAMPLE SECTIONS:
- Introduction/Background
- Current State Analysis
- Key Findings/Developments
- Challenges and Limitations
- Future Implications
- Conclusion

Generate a comprehensive research plan now.""",
            variables=["topic", "depth", "sources", "time_limit", "audience"],
            description="Creates a structured research plan for any given topic",
            example_input={
                "topic": "AI Ethics in Healthcare",
                "depth": "comprehensive",
                "sources": ["web", "academic", "news"],
                "time_limit": "30 minutes",
                "audience": "general"
            },
            expected_output="JSON with research plan structure"
        )
        
        # Researcher Agent Prompts
        self.templates["web_researcher"] = PromptTemplate(
            name="web_researcher",
            type=PromptType.RESEARCHER,
            template="""You are a Web Research Agent. Your task is to gather and analyze information from web sources for a specific research section.

RESEARCH SECTION: {section}
MAIN TOPIC: {topic}
SEARCH RESULTS: {search_results}

CONTEXT:
- Research focus: {focus}
- Required depth: {depth}
- Source quality threshold: {quality_threshold}

INSTRUCTIONS:
1. Analyze the provided search results for relevance and credibility
2. Extract key information related to the research section
3. Identify the most important findings and insights
4. Note any conflicting information or gaps
5. Assess the quality and reliability of sources

OUTPUT FORMAT:
Provide a structured response with:
- "key_findings": List of main discoveries/insights
- "supporting_evidence": Relevant quotes and data points
- "source_analysis": Assessment of source credibility
- "information_gaps": Areas needing more research
- "confidence_score": Your confidence in the findings (0-1)
- "summary": Concise summary of the section content

Focus on accuracy, relevance, and providing actionable insights.""",
            variables=["section", "topic", "search_results", "focus", "depth", "quality_threshold"],
            description="Analyzes web search results for a specific research section",
            example_input={
                "section": "Current Applications",
                "topic": "AI in Healthcare",
                "search_results": "[search results data]",
                "focus": "practical applications",
                "depth": "detailed",
                "quality_threshold": "0.7"
            },
            expected_output="Structured analysis of web research findings"
        )
        
        self.templates["academic_researcher"] = PromptTemplate(
            name="academic_researcher",
            type=PromptType.RESEARCHER,
            template="""You are an Academic Research Agent. Your task is to analyze academic papers and research for a specific research section.

RESEARCH SECTION: {section}
MAIN TOPIC: {topic}
ACADEMIC SOURCES: {academic_sources}

CONTEXT:
- Research methodology focus: {methodology}
- Publication date range: {date_range}
- Academic rigor required: {rigor_level}

INSTRUCTIONS:
1. Analyze academic papers for methodological soundness
2. Extract key research findings and conclusions
3. Identify research trends and patterns
4. Note limitations and future research directions
5. Assess the strength of evidence

OUTPUT FORMAT:
Provide a scholarly analysis with:
- "research_findings": Key discoveries from academic sources
- "methodologies": Research methods used in studies
- "evidence_strength": Assessment of evidence quality
- "research_gaps": Identified gaps in current research
- "future_directions": Suggested areas for future study
- "citation_summary": Brief summary of key papers
- "confidence_score": Confidence in academic evidence (0-1)

Maintain academic rigor and cite specific studies when relevant.""",
            variables=["section", "topic", "academic_sources", "methodology", "date_range", "rigor_level"],
            description="Analyzes academic sources for research sections",
            example_input={
                "section": "Research Methods",
                "topic": "Machine Learning in Diagnostics",
                "academic_sources": "[academic papers data]",
                "methodology": "empirical",
                "date_range": "2020-2024",
                "rigor_level": "high"
            },
            expected_output="Academic analysis with research findings and methodology assessment"
        )
        
        # Writer Agent Prompts
        self.templates["report_writer"] = PromptTemplate(
            name="report_writer",
            type=PromptType.WRITER,
            template="""You are a Report Writing Agent. Your task is to compile research data into a well-structured, comprehensive report.

TOPIC: {topic}
RESEARCH DATA: {research_data}
TARGET AUDIENCE: {audience}
REPORT LENGTH: {length}

CONTEXT:
- Writing style: {style}
- Technical level: {technical_level}
- Include citations: {include_citations}

INSTRUCTIONS:
1. Create a logical flow of information
2. Write clear, engaging content appropriate for the audience
3. Integrate findings from multiple sources seamlessly
4. Maintain objectivity while highlighting key insights
5. Include proper section headings and structure
6. Add citations and references where appropriate

OUTPUT FORMAT:
Generate a complete report with:
- Executive Summary
- Introduction
- Main Content Sections (based on research data)
- Key Findings/Conclusions
- References (if citations enabled)

WRITING GUIDELINES:
- Use clear, concise language
- Support claims with evidence
- Maintain consistent tone throughout
- Include transitions between sections
- Highlight important insights
- Ensure factual accuracy

Write a comprehensive report now.""",
            variables=["topic", "research_data", "audience", "length", "style", "technical_level", "include_citations"],
            description="Compiles research data into a structured report",
            example_input={
                "topic": "AI Ethics Implementation",
                "research_data": "[compiled research findings]",
                "audience": "business executives",
                "length": "medium",
                "style": "professional",
                "technical_level": "moderate",
                "include_citations": "true"
            },
            expected_output="Complete structured report with all sections"
        )
        
        # Analyzer Agent Prompts
        self.templates["data_analyzer"] = PromptTemplate(
            name="data_analyzer",
            type=PromptType.ANALYZER,
            template="""You are a Data Analysis Agent. Your task is to analyze research data and identify patterns, trends, and insights.

RESEARCH DATA: {data}
ANALYSIS FOCUS: {focus}
ANALYSIS TYPE: {analysis_type}

CONTEXT:
- Data sources: {sources}
- Time period: {time_period}
- Analysis depth: {depth}

INSTRUCTIONS:
1. Examine the data for patterns and trends
2. Identify correlations and relationships
3. Look for anomalies or unexpected findings
4. Assess data quality and reliability
5. Draw meaningful conclusions

OUTPUT FORMAT:
Provide analysis results with:
- "patterns_identified": Key patterns found in the data
- "trends": Temporal or categorical trends
- "correlations": Relationships between variables
- "anomalies": Unexpected or outlying data points
- "insights": Key insights and implications
- "confidence_level": Confidence in analysis (0-1)
- "recommendations": Suggested actions based on analysis

Focus on actionable insights and clear explanations.""",
            variables=["data", "focus", "analysis_type", "sources", "time_period", "depth"],
            description="Analyzes research data to identify patterns and insights",
            example_input={
                "data": "[research dataset]",
                "focus": "market trends",
                "analysis_type": "trend analysis",
                "sources": "multiple",
                "time_period": "2020-2024",
                "depth": "comprehensive"
            },
            expected_output="Detailed analysis with patterns, trends, and insights"
        )
        
        # Summarizer Agent Prompts
        self.templates["content_summarizer"] = PromptTemplate(
            name="content_summarizer",
            type=PromptType.SUMMARIZER,
            template="""You are a Content Summarization Agent. Your task is to create concise, accurate summaries of research content.

CONTENT TO SUMMARIZE: {content}
SUMMARY TYPE: {summary_type}
TARGET LENGTH: {target_length}

CONTEXT:
- Key focus areas: {focus_areas}
- Audience level: {audience_level}
- Include key statistics: {include_stats}

INSTRUCTIONS:
1. Identify the most important information
2. Preserve key facts, figures, and conclusions
3. Maintain the original meaning and context
4. Use clear, concise language
5. Organize information logically

OUTPUT FORMAT:
Provide a summary with:
- "main_points": List of key points covered
- "key_statistics": Important numbers and data
- "conclusions": Main conclusions or findings
- "summary_text": The actual summary content
- "coverage_score": How well the summary covers the original (0-1)

SUMMARY TYPES:
- "executive": High-level overview for executives
- "technical": Detailed summary for technical audience
- "general": Accessible summary for general audience
- "bullet": Key points in bullet format

Create an effective summary now.""",
            variables=["content", "summary_type", "target_length", "focus_areas", "audience_level", "include_stats"],
            description="Creates concise summaries of research content",
            example_input={
                "content": "[research content to summarize]",
                "summary_type": "executive",
                "target_length": "200 words",
                "focus_areas": "key findings, recommendations",
                "audience_level": "executive",
                "include_stats": "true"
            },
            expected_output="Concise summary with key points and statistics"
        )
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a specific prompt template"""
        return self.templates.get(template_name)
    
    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type"""
        return [template for template in self.templates.values() if template.type == prompt_type]
    
    def generate_prompt(self, template_name: str, **kwargs) -> str:
        """Generate a prompt from a template with provided variables"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing required variable '{missing_var}' for template '{template_name}'")
    
    def validate_template_variables(self, template_name: str, variables: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        missing_variables = []
        for var in template.variables:
            if var not in variables:
                missing_variables.append(var)
        
        return missing_variables
    
    def add_custom_template(self, template: PromptTemplate) -> None:
        """Add a custom prompt template"""
        self.templates[template.name] = template
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template"""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            "name": template.name,
            "type": template.type.value,
            "description": template.description,
            "variables": template.variables,
            "example_input": template.example_input
        }

# Global prompt manager instance
_global_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """Get or create global prompt manager instance"""
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager()
    return _global_prompt_manager

def generate_prompt(template_name: str, **kwargs) -> str:
    """Convenience function to generate a prompt"""
    manager = get_prompt_manager()
    return manager.generate_prompt(template_name, **kwargs) 