
import streamlit as st
from datetime import datetime
import config
from database import database
from research_agent import research_agent
from agents.cache_manager import cache
from agents.export_agent import export_agent
from database.database import db
from utils.error_handler import logger
import io
import sys
sys.path.append('..')
from components.navbar import render_navbar
from components.footer import render_footer

st.set_page_config(page_title="Search Papers", page_icon=None, layout="wide")

# Apply dark mode if enabled
if st.session_state.get('dark_mode', False):
    st.markdown("""
        <style>
        .stApp { background-color: #1E1E1E; color: #E0E0E0; }
        .stMarkdown, .stText { color: #E0E0E0; }
        </style>
    """, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .paper-card {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .status-success { background-color: #28a745; color: white; }
    .status-failed { background-color: #dc3545; color: white; }
    .status-pending { background-color: #ffc107; color: black; }
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
    }
    .source-semantic { background-color: #e3f2fd; color: #1976d2; }
    .source-arxiv { background-color: #f3e5f5; color: #7b1fa2; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

def main():
    render_navbar(current_page="Search")
    
    st.title("Search Academic Papers")
    st.markdown("Search across multiple databases with AI-powered analysis")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Search Configuration")
        
        # Database selection
        st.subheader("Databases")
        use_semantic_scholar = st.checkbox("Semantic Scholar", value=True)
        use_arxiv = st.checkbox("ArXiv", value=True)
        
        databases = []
        if use_semantic_scholar:
            databases.append('semantic_scholar')
        if use_arxiv:
            databases.append('arxiv')
        
        st.divider()
        
        # Search settings
        st.subheader("Settings")
        limit = st.slider("Number of papers", 1, config.MAX_PAPER_LIMIT, 10)
        
        summary_level = st.selectbox(
            "Summary Detail",
            options=list(config.SUMMARY_LEVELS.keys()),
            index=1,
            format_func=lambda x: f"{x.title()} - {config.SUMMARY_LEVELS[x]['description']}"
        )
        
        process_pdfs = st.checkbox("Process PDFs", value=True,
                                   help="Download and analyze full papers (slower but more detailed)")
        
        st.divider()
        
        # Filters
        st.subheader("Filters")
        
        col1, col2 = st.columns(2)
        with col1:
            year_from = st.number_input("Year from", min_value=1900, max_value=2025, value=None)
        with col2:
            year_to = st.number_input("Year to", min_value=1900, max_value=2025, value=None)
        
        open_access_only = st.checkbox("Open Access Only", value=False)
        
        st.divider()
        
        # Save to project
        st.subheader("Save Results")
        projects = db.get_all_projects()
        project_options = ["Don't save"] + [f"{p.name} (ID: {p.id})" for p in projects]
        selected_project = st.selectbox("Save to project", project_options)
        
        if selected_project != "Don't save":
            project_id = int(selected_project.split("ID: ")[1].rstrip(")"))
            st.session_state.current_project = project_id
        
        st.divider()
        
        # Cache management
        st.subheader("Cache")
        cache_stats = cache.get_cache_stats()
        st.metric("Cached Items", cache_stats['topic_cache_files'] + cache_stats['paper_cache_files'])
        
        if st.button("Clear Cache", use_container_width=True):
            cache.clear_all_cache()
            st.success("Cache cleared!")
    
    # Main search interface
    st.divider()
    
    # Search bar
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "Enter your research topic",
            placeholder="e.g., 'machine learning for drug discovery'",
            label_visibility="collapsed"
        )
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    # Example queries
    with st.expander("Example Queries"):
        examples = [
            "transformer models in natural language processing",
            "CRISPR gene editing applications",
            "quantum computing algorithms",
            "climate change machine learning",
            "deep learning protein structure prediction"
        ]
        cols = st.columns(3)
        for i, example in enumerate(examples):
            with cols[i % 3]:
                if st.button(example, key=f"example_{i}"):
                    st.session_state.search_query = example
                    st.rerun()
    
    # Process search
    if search_button or st.session_state.get('search_query'):
        if st.session_state.get('search_query'):
            query = st.session_state.search_query
            st.session_state.search_query = None
        
        if not query:
            st.warning("Please enter a search topic")
            return
        
        if not databases:
            st.warning("Please select at least one database")
            return
        
        # Perform search
        with st.spinner(f"Searching for papers on '{query}'..."):
            try:
                start_time = datetime.now()
                
                papers = research_agent.search_and_analyze(
                    query=query,
                    limit=limit,
                    summary_level=summary_level,
                    process_pdfs=process_pdfs,
                    year_from=year_from,
                    year_to=year_to,
                    open_access_only=open_access_only,
                    # databases=database
                    # databases=databases
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if papers:
                    st.session_state.search_results = papers
                    
                    # Save to database
                    db.save_search({
                        'query': query,
                        'limit': limit,
                        'summary_level': summary_level,
                        'year_from': year_from,
                        'year_to': year_to,
                        'open_access_only': open_access_only,
                        'databases': databases,
                        'results_count': len(papers),
                        'papers_found': [p.get('paper_id') for p in papers],
                        'search_duration_seconds': duration
                    })
                    
                    # Save papers to project if selected
                    if st.session_state.current_project:
                        for paper in papers:
                            # Save paper to database first
                            db_paper = db.create_or_update_paper(paper)
                            if db_paper:
                                db.add_paper_to_project(
                                    st.session_state.current_project,
                                    db_paper.id
                                )
                    
                    st.success(f"Found {len(papers)} papers in {duration:.1f}s")
                else:
                    st.error("No papers found. Try different keywords.")
                    return
                    
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
                logger.error(f"Search error: {str(e)}")
                return
    
    # Display results
    if st.session_state.search_results:
        papers = st.session_state.search_results
        
        st.divider()
        
        # Results header with actions
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.header(f"Results ({len(papers)} papers)")
        with col2:
            # Sort options
            sort_by = st.selectbox(
                "Sort by",
                ["Relevance", "Year (Newest)", "Year (Oldest)", "Citations"],
                label_visibility="collapsed"
            )
        with col3:
            # Export all button
            export_format = st.selectbox(
                "Export format",
                ["Word", "PDF", "CSV", "BibTeX", "Markdown", "LaTeX", "JSON"],
                label_visibility="collapsed"
            )
        with col4:
            if st.button("📥 Export All", use_container_width=True):
                export_results(papers, export_format)
        
        # Sort papers
        if sort_by == "Year (Newest)":
            papers = sorted(papers, key=lambda x: x.get('year', 0) if isinstance(x.get('year'), int) else 0, reverse=True)
        elif sort_by == "Year (Oldest)":
            papers = sorted(papers, key=lambda x: x.get('year', 0) if isinstance(x.get('year'), int) else 0)
        elif sort_by == "Citations":
            papers = sorted(papers, key=lambda x: x.get('citation_count', 0), reverse=True)
        
        # Display papers
        for i, paper in enumerate(papers, 1):
            display_paper(paper, i)


def display_paper(paper, index):
    """Display a single paper card"""
    with st.container():
        # Paper header
        col1, col2 = st.columns([5, 1])
        with col1:
            # Source badge
            source = paper.get('source', 'unknown')
            source_class = f"source-{source}"
            st.markdown(f'<span class="source-badge {source_class}">{source.upper()}</span>', unsafe_allow_html=True)
            
            # Title
            st.markdown(f"### {index}. {paper.get('title', 'Untitled')}")
            
            # Metadata
            authors = ", ".join(paper.get('authors', [])[:3])
            if len(paper.get('authors', [])) > 3:
                authors += " et al."
            
            year = paper.get('year', 'Unknown')
            venue = paper.get('venue', 'Unknown')
            citations = paper.get('citation_count', 0)
            
            st.markdown(f"**{authors}** • {year} • {venue} • {citations} citations")
        
        with col2:
            st.markdown(f"[View Paper]({paper.get('url', '#')})")
        
        # Tabs
        tabs = st.tabs(["Summary", "Analysis", "Export", "Actions"])
        
        with tabs[0]:  # Summary
            if paper.get('abstract_summary'):
                st.write("**AI Summary:**")
                st.write(paper['abstract_summary'])
            
            if paper.get('abstract'):
                with st.expander("View full abstract"):
                    st.write(paper['abstract'])
        
        with tabs[1]:  # Analysis
            if paper.get('key_findings'):
                st.write("**Key Findings:**")
                st.write(paper['key_findings'])
            
            if paper.get('research_gaps'):
                gaps = paper['research_gaps']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Methodology Gaps:**")
                    st.write(gaps.get('methodology_gaps', 'N/A'))
                with col2:
                    st.write("**Knowledge Gaps:**")
                    st.write(gaps.get('knowledge_gaps', 'N/A'))
                
                st.write("**Future Directions:**")
                st.write(gaps.get('future_directions', 'N/A'))
        
        with tabs[2]:  # Export
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Word", key=f"word_{index}", use_container_width=True):
                    export_single_paper(paper, "Word")
            with col2:
                if st.button("📑 PDF", key=f"pdf_{index}", use_container_width=True):
                    export_single_paper(paper, "PDF")
            with col3:
                if st.button("📋 BibTeX", key=f"bib_{index}", use_container_width=True):
                    export_single_paper(paper, "BibTeX")
        
        with tabs[3]:  # Actions
            col1, col2 = st.columns(2)
            
            with col1:
                # Add to project
                projects = db.get_all_projects()
                if projects:
                    project = st.selectbox(
                        "Add to project",
                        ["Select project..."] + [p.name for p in projects],
                        key=f"project_{index}"
                    )
                    if project != "Select project..." and st.button("Add", key=f"add_{index}"):
                        selected_project = next(p for p in projects if p.name == project)
                        db_paper = db.create_or_update_paper(paper)
                        if db_paper:
                            db.add_paper_to_project(selected_project.id, db_paper.id)
                            st.success(f"Added to {project}!")
            
            with col2:
                # Copy citation
                citation = research_agent.generate_citation(paper, "APA")
                st.text_area("Citation", citation, height=100, key=f"cite_{index}")
        
        st.divider()
    
    # Render footer
    render_footer()


def export_single_paper(paper, format_type):
    """Export a single paper"""
    try:
        if format_type == "Word":
            doc = export_agent.export_to_word([paper])
            st.download_button(
                "📥 Download Word",
                doc,
                file_name=f"{paper.get('title', 'paper')[:50]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        elif format_type == "PDF":
            pdf = export_agent.export_to_pdf([paper])
            st.download_button(
                "📥 Download PDF",
                pdf,
                file_name=f"{paper.get('title', 'paper')[:50]}.pdf",
                mime="application/pdf"
            )
        elif format_type == "BibTeX":
            bib = export_agent.export_to_bibtex([paper])
            st.download_button(
                "📥 Download BibTeX",
                bib,
                file_name=f"{paper.get('title', 'paper')[:50]}.bib",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"Export failed: {str(e)}")


def export_results(papers, format_type):
    """Export all search results"""
    try:
        if format_type == "Word":
            doc = export_agent.export_to_word(papers)
            st.download_button(
                "📥 Download All (Word)",
                doc,
                file_name="search_results.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        elif format_type == "PDF":
            pdf = export_agent.export_to_pdf(papers)
            st.download_button(
                "📥 Download All (PDF)",
                pdf,
                file_name="search_results.pdf",
                mime="application/pdf"
            )
        elif format_type == "CSV":
            csv = export_agent.export_to_csv(papers)
            st.download_button(
                "📥 Download All (CSV)",
                csv.getvalue(),
                file_name="search_results.csv",
                mime="text/csv"
            )
        elif format_type == "BibTeX":
            bib = export_agent.export_to_bibtex(papers)
            st.download_button(
                "📥 Download All (BibTeX)",
                bib,
                file_name="search_results.bib",
                mime="text/plain"
            )
        elif format_type == "Markdown":
            md = export_agent.export_to_markdown(papers)
            st.download_button(
                "📥 Download All (Markdown)",
                md,
                file_name="search_results.md",
                mime="text/markdown"
            )
        elif format_type == "LaTeX":
            latex = export_agent.export_to_latex(papers)
            st.download_button(
                "📥 Download All (LaTeX)",
                latex,
                file_name="search_results.tex",
                mime="text/plain"
            )
        elif format_type == "JSON":
            json = export_agent.export_to_json(papers)
            st.download_button(
                "📥 Download All (JSON)",
                json,
                file_name="search_results.json",
                mime="application/json"
            )
        
        st.success(f"Exported {len(papers)} papers!")
    except Exception as e:
        st.error(f"Export failed: {str(e)}")


if __name__ == "__main__":
    main()