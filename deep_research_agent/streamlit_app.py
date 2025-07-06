import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Import backend modules
from orchestrator.manager import AgentManager
from memory import MemoryManager
from utils.chain_of_thought import LogLevel

st.set_page_config(page_title="Deep Research Agent", layout="wide")

# Initialize session state
if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = AgentManager()
if 'memory_manager' not in st.session_state:
    st.session_state.memory_manager = MemoryManager()
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'research_in_progress' not in st.session_state:
    st.session_state.research_in_progress = False

st.title("🔍 Deep Research Agent")

# Sidebar: Settings/API Keys
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("API Configuration"):
        serpapi_key = st.text_input("SerpAPI Key", type="password", 
                                   help="Required for web search functionality")
        openai_key = st.text_input("OpenAI API Key", type="password",
                                  help="Required for LLM processing")
        arxiv_key = st.text_input("ArXiv API Key", type="password",
                                 help="Optional - for enhanced academic search")
        pubmed_key = st.text_input("PubMed API Key", type="password",
                                  help="Optional - for enhanced medical research")
    
    st.markdown("---")
    
    with st.expander("Research Settings"):
        max_results = st.slider("Max Results per Source", 5, 20, 10)
        include_academic = st.checkbox("Include Academic Sources", value=True)
        include_news = st.checkbox("Include News Sources", value=True)
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    
    # Memory controls
    st.subheader("🧠 Memory Controls")
    if st.button("Clear Short-term Memory"):
        st.session_state.memory_manager.short_term.clear_memory()
        st.success("Short-term memory cleared!")
    
    if st.button("Clear Session Logs"):
        cleared = st.session_state.agent_manager.cot_logger.clear_logs(
            st.session_state.agent_manager.session_id
        )
        st.success(f"Cleared {cleared} log entries!")
    
    # Display API status
    st.markdown("---")
    st.subheader("🔗 API Status")
    api_status = {
        "SerpAPI": "✅ Ready" if serpapi_key else "❌ Not configured",
        "OpenAI": "✅ Ready" if openai_key else "❌ Not configured",
        "ArXiv": "✅ Ready" if arxiv_key else "⚠️ Optional",
        "PubMed": "✅ Ready" if pubmed_key else "⚠️ Optional"
    }
    
    for api, status in api_status.items():
        st.text(f"{api}: {status}")

# Main input area
st.subheader("📝 Research Topic")
col1, col2 = st.columns([4, 1])

with col1:
    topic = st.text_input("Enter your research topic or question:", 
                         placeholder="e.g., 'Impact of AI on healthcare industry'",
                         disabled=st.session_state.research_in_progress)

with col2:
    start_btn = st.button("🚀 Start Research", 
                         disabled=st.session_state.research_in_progress or not topic)

# Handle research start
if start_btn and topic:
    st.session_state.research_in_progress = True
    st.session_state.research_results = None
    
    # Add to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": f"Research topic: {topic}",
        "timestamp": datetime.now().isoformat()
    })
    
    # Add to memory
    st.session_state.memory_manager.add_conversation_message({
        "role": "user",
        "content": f"Research request: {topic}",
        "timestamp": datetime.now().isoformat()
    })
    
    # Start research
    with st.spinner("🔍 Conducting research... This may take a few minutes."):
        try:
            results = st.session_state.agent_manager.start_research(topic)
            st.session_state.research_results = results
            
            # Add results to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Research completed! Generated {len(results.get('plan', {}).get('sections', []))} sections.",
                "timestamp": datetime.now().isoformat()
            })
            
            # Store important findings in long-term memory
            if results.get('success'):
                st.session_state.memory_manager.store_important_memory(
                    content=f"Research on {topic}: {results.get('report', '')[:500]}...",
                    metadata={"topic": topic, "session_id": results.get('session_id')},
                    importance=0.9
                )
            
        except Exception as e:
            st.error(f"Research failed: {str(e)}")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Research failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    st.session_state.research_in_progress = False

st.markdown("---")

# Layout: 3 columns for main panels
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("💬 Chat Panel")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if st.session_state.chat_history:
            for i, msg in enumerate(st.session_state.chat_history[-10:]):  # Show last 10 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                
                if role == 'user':
                    st.markdown(f"**👤 You** ({timestamp[:16]})")
                    st.markdown(f"> {content}")
                else:
                    st.markdown(f"**🤖 Agent** ({timestamp[:16]})")
                    st.markdown(f"> {content}")
                st.markdown("---")
        else:
            st.info("No conversation history yet. Start a research to begin!")
    
    # Chat input
    user_input = st.text_input("Ask a question about the research:", 
                              placeholder="e.g., 'Can you explain the methodology?'")
    
    if user_input and st.session_state.research_results:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get relevant context from memory
        context = st.session_state.memory_manager.get_relevant_context(user_input)
        
        # Simple response based on context
        response = f"Based on the research, here's what I found: {user_input}"
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        st.rerun()

with col2:
    st.subheader("📊 Report Panel")
    
    if st.session_state.research_results:
        results = st.session_state.research_results
        
        # Display success/failure status
        if results.get('success'):
            st.success("✅ Research completed successfully!")
            
            # Display research plan
            if results.get('plan'):
                with st.expander("📋 Research Plan"):
                    plan = results['plan']
                    st.write(f"**Sections:** {', '.join(plan.get('sections', []))}")
                    st.write(f"**Approaches:** {', '.join(plan.get('research_approaches', []))}")
                    st.write(f"**Estimated Time:** {plan.get('estimated_time', 'Unknown')}")
            
            # Display final report
            if results.get('report'):
                st.markdown("### 📄 Final Report")
                st.markdown(results['report'])
            
            # Display research data summary
            if results.get('data'):
                with st.expander("🔍 Research Data Summary"):
                    data = results['data']
                    for section, content in data.items():
                        st.write(f"**{section}:**")
                        if isinstance(content, dict):
                            st.write(f"- Content: {content.get('content', 'N/A')[:100]}...")
                            st.write(f"- Sources: {len(content.get('sources', []))}")
                            st.write(f"- Confidence: {content.get('confidence', 0):.2f}")
                        else:
                            st.write(f"- {str(content)[:100]}...")
                        st.write("---")
        else:
            st.error("❌ Research failed!")
            st.error(results.get('error', 'Unknown error'))
    else:
        st.info("📝 Research report will appear here after you start a research.")
        st.markdown("""
        **What you'll see here:**
        - Research plan and sections
        - Final compiled report
        - Source summaries
        - Data confidence scores
        """)

with col3:
    st.subheader("🧠 Chain-of-Thought")
    
    if st.session_state.research_results:
        cot_summary = st.session_state.research_results.get('chain_of_thought', {})
        
        # Display summary
        st.metric("Total Steps", cot_summary.get('total_steps', 0))
        st.metric("Avg Confidence", f"{cot_summary.get('average_confidence', 0):.2f}")
        
        # Display agents involved
        agents = cot_summary.get('agents_involved', [])
        if agents:
            st.write("**Agents Used:**")
            for agent in agents:
                st.write(f"- {agent}")
        
        # Display tools used
        tools = cot_summary.get('tools_used', [])
        if tools:
            st.write("**Tools Used:**")
            for tool in tools:
                st.write(f"- {tool}")
        
        # Display key decisions
        decisions = cot_summary.get('key_decisions', [])
        if decisions:
            with st.expander("🎯 Key Decisions"):
                for decision in decisions:
                    st.write(f"**{decision.get('agent')}:** {decision.get('decision')}")
                    st.write(f"Confidence: {decision.get('confidence', 0):.2f}")
                    st.write("---")
        
        # Detailed logs
        if st.button("📋 Show Detailed Logs"):
            detailed_logs = st.session_state.agent_manager.get_detailed_logs()
            
            for log in detailed_logs:
                with st.expander(f"{log.get('agent')} - {log.get('timestamp', '')[:16]}"):
                    st.json(log)
    else:
        st.info("🤔 Agent reasoning will be shown here during research.")
    
    st.markdown("---")
    st.subheader("💾 Memory Panel")
    
    # Short-term memory
    with st.expander("📝 Short-term Memory"):
        memory_summary = st.session_state.memory_manager.short_term.summarize_conversation()
        st.write(f"**Total Messages:** {memory_summary.get('total_messages', 0)}")
        st.write(f"**Time Span:** {memory_summary.get('time_span', 'N/A')}")
        
        key_topics = memory_summary.get('key_topics', [])
        if key_topics:
            st.write(f"**Key Topics:** {', '.join(key_topics)}")
        
        # Recent messages
        recent_messages = st.session_state.memory_manager.short_term.get_messages(5)
        if recent_messages:
            st.write("**Recent Messages:**")
            for msg in recent_messages[-3:]:  # Show last 3
                st.write(f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
    
    # Long-term memory
    with st.expander("🗄️ Long-term Memory"):
        lt_stats = st.session_state.memory_manager.long_term.get_memory_stats()
        st.write(f"**Total Memories:** {lt_stats.get('total_memories', 0)}")
        st.write(f"**Vector Store:** {lt_stats.get('vector_store', 'Unknown')}")
        
        # Memory search
        search_query = st.text_input("Search memories:", placeholder="Enter search terms...")
        if search_query:
            memories = st.session_state.memory_manager.long_term.retrieve_memories(search_query, limit=3)
            if memories:
                st.write("**Search Results:**")
                for memory in memories:
                    st.write(f"- {memory.get('content', '')[:100]}...")
            else:
                st.write("No matching memories found.")

# Footer
st.markdown("---")
st.markdown("*Deep Research Agent - Powered by AI and Chain-of-Thought Reasoning*") 