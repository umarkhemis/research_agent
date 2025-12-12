import streamlit as st
from datetime import datetime
import config
from database.database import db
from agents.literature_review_agent import lit_review_agent
from utils.error_handler import logger
import sys
sys.path.append('..')
from components.navbar import render_navbar
from components.footer import render_footer

st.set_page_config(page_title="Literature Review", page_icon=None, layout="wide")

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
    .review-preview {
        background-color: var(--background-color);
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #7b1fa2;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
    }
    .stat-box {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .step-card {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4A9EFF;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_review' not in st.session_state:
    st.session_state.generated_review = None
if 'review_papers' not in st.session_state:
    st.session_state.review_papers = []


def main():
    render_navbar(current_page="Review")
    
    st.title("Literature Review Generator")
    st.markdown("Generate comprehensive literature reviews in minutes, powered by AI")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Review Configuration")
        
        # Source selection
        st.subheader("Paper Source")
        source = st.radio(
            "Select papers from",
            ["Recent Search", "Saved Project", "Custom Selection"],
            label_visibility="collapsed"
        )
        
        selected_papers = []
        
        if source == "Recent Search":
            if st.session_state.get('search_results'):
                selected_papers = st.session_state.search_results
                st.success(f"{len(selected_papers)} papers from last search")
            else:
                st.warning("No recent search. Go to Search page first.")
        
        elif source == "Saved Project":
            projects = db.get_all_projects()
            if projects:
                project_names = [p.name for p in projects]
                selected_project_name = st.selectbox("Select project", project_names)
                selected_project = next(p for p in projects if p.name == selected_project_name)
                
                papers = db.get_project_papers(selected_project.id)
                # Convert to dict format
                selected_papers = []
                for paper in papers:
                    paper_dict = {
                        'title': paper.title,
                        'authors': paper.authors or [],
                        'year': paper.year,
                        'abstract': paper.abstract,
                        'abstract_summary': paper.abstract_summary_medium,
                        'key_findings': paper.key_findings,
                        'research_gaps': {
                            'methodology_gaps': paper.methodology_gaps,
                            'knowledge_gaps': paper.knowledge_gaps,
                            'future_directions': paper.future_directions
                        }
                    }
                    selected_papers.append(paper_dict)
                
                st.success(f"{len(selected_papers)} papers from project")
            else:
                st.warning("No projects yet. Create one first.")
        
        st.session_state.review_papers = selected_papers
        
        st.divider()
        
        # Review settings
        st.subheader("Review Settings")
        
        detail_level = st.select_slider(
            "Detail Level",
            options=["short", "medium", "long"],
            value="medium",
            format_func=lambda x: x.title()
        )
        
        st.caption(config.LIT_REVIEW_DETAIL_LEVELS[detail_level]["description"])
        
        review_type = st.selectbox(
            "Organization Type",
            options=config.LIT_REVIEW_TYPES,
            format_func=lambda x: x.title()
        )
        
        st.divider()
        
        # Additional options
        st.subheader("Options")
        save_to_db = st.checkbox("Save to database", value=True)
        
        if save_to_db:
            projects = db.get_all_projects()
            if projects:
                project_names = ["None"] + [p.name for p in projects]
                selected_proj = st.selectbox("Associate with project", project_names)
                if selected_proj != "None":
                    st.session_state.review_project = next(p.id for p in projects if p.name == selected_proj)
                else:
                    st.session_state.review_project = None
            else:
                st.session_state.review_project = None
    
    # Main content
    if not st.session_state.review_papers:
        show_getting_started()
    elif st.session_state.generated_review:
        show_review_results(st.session_state.generated_review)
    else:
        show_generation_interface(detail_level, review_type, save_to_db)
    
    # Render footer
    render_footer()


def show_getting_started():
    """Show getting started guide"""
    st.info("👋 Welcome to the Literature Review Generator!")
    
    st.markdown("""
    ### How It Works:
    
    1. **Select Papers** - Choose papers from your recent search or a saved project
    2. **Configure** - Select detail level and organization type
    3. **Generate** - AI creates a comprehensive literature review
    4. **Export** - Download in multiple formats (Word, PDF, LaTeX, etc.)
    
    ### What You Get:
    
    - Introduction with context and scope
    - Thematic analysis of papers
    - Methodological approaches overview
    - Synthesis of key findings
    - Research gaps and future directions
    - Conclusion and references
    
    **Time savings:** Write in 10 minutes what takes 30-50 hours manually!
    """)
    
    st.markdown("---")
    
    # Quick action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Start with Search")
        st.write("Search for papers and generate review from results")
        if st.button("Go to Search →", use_container_width=True):
            st.switch_page("pages/Search.py")
    
    with col2:
        st.subheader("Use Existing Project")
        st.write("Generate review from papers in your projects")
        if st.button("Go to Projects →", use_container_width=True):
            st.switch_page("pages/Projects.py")


def show_generation_interface(detail_level, review_type, save_to_db):
    """Show the generation interface"""
    papers = st.session_state.review_papers
    
    # Paper preview
    st.header(f"Selected Papers ({len(papers)})")
    
    # Paper quality check
    papers_with_summaries = sum(1 for p in papers if p.get('abstract_summary') or p.get('abstract'))
    papers_with_gaps = sum(1 for p in papers if p.get('research_gaps'))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Papers", len(papers))
    with col2:
        st.metric("With Summaries", papers_with_summaries)
    with col3:
        st.metric("With Gap Analysis", papers_with_gaps)
    with col4:
        quality_score = int((papers_with_summaries / len(papers)) * 100)
        st.metric("Quality Score", f"{quality_score}%")
    
    if quality_score < 50:
        st.warning("Low quality score. Consider processing PDFs for better results.")
    
    # Paper list preview
    with st.expander("View Paper List"):
        for i, paper in enumerate(papers[:10], 1):
            st.write(f"{i}. **{paper.get('title', 'Untitled')}** ({paper.get('year', 'N/A')})")
        if len(papers) > 10:
            st.write(f"... and {len(papers) - 10} more")
    
    st.divider()
    
    # Review configuration preview
    st.header("Review Configuration")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f"**Detail Level**")
        st.markdown(f"{detail_level.title()}")
        st.caption(config.LIT_REVIEW_DETAIL_LEVELS[detail_level]["description"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f"**Organization**")
        st.markdown(f"{review_type.title()}")
        st.caption("How papers will be organized")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        est_words = config.LIT_REVIEW_DETAIL_LEVELS[detail_level]["target_words"]
        est_pages = est_words // 250
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f"**Estimated Output**")
        st.markdown(f"{est_pages}-{est_pages+2} pages")
        st.caption(f"~{est_words} words")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Generate button
    st.header("Generate Review")
    
    # Topic input
    topic = st.text_input(
        "Review Topic/Title",
        placeholder="e.g., Machine Learning for Drug Discovery",
        help="This will be used as the title and focus of the review"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("Generate Literature Review", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a review topic")
            elif len(papers) < 3:
                st.error("Need at least 3 papers to generate a review")
            else:
                generate_review(topic, papers, detail_level, review_type, save_to_db)
    
    with col2:
        st.caption("")  # Spacing
    
    with col3:
        st.caption("Est. time: 1-2 min")


def generate_review(topic, papers, detail_level, review_type, save_to_db):
    """Generate the literature review"""
    
    with st.spinner("Generating literature review... This may take 1-2 minutes..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Detect themes
            status_text.text("Detecting themes across papers...")
            progress_bar.progress(20)
            
            # Step 2: Generate review
            status_text.text("Writing literature review sections...")
            progress_bar.progress(40)
            
            project_id = st.session_state.get('review_project')
            
            review_result = lit_review_agent.generate_review(
                papers=papers,
                query=topic,
                detail_level=detail_level,
                review_type=review_type,
                project_id=project_id,
                save_to_db=save_to_db
            )
            
            progress_bar.progress(80)
            status_text.text("Finalizing review...")
            
            progress_bar.progress(100)
            status_text.text("Review generated successfully!")
            
            st.session_state.generated_review = review_result
            st.rerun()
            
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
            logger.error(f"Literature review generation error: {str(e)}")


def show_review_results(review_result):
    """Display the generated review"""
    st.success("Literature Review Generated!")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Word Count", f"{review_result['word_count']:,}")
    with col2:
        st.metric("Estimated Pages", review_result['page_estimate'])
    with col3:
        st.metric("Papers Included", review_result['papers_count'])
    with col4:
        reading_time = review_result['word_count'] // 200
        st.metric("Reading Time", f"{reading_time} min")
    
    st.divider()
    
    # Export options
    st.header("Export Review")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("Word", use_container_width=True):
            export_review(review_result, "word")
    with col2:
        if st.button("PDF", use_container_width=True):
            export_review(review_result, "pdf")
    with col3:
        if st.button("Markdown", use_container_width=True):
            export_review(review_result, "markdown")
    with col4:
        if st.button("LaTeX", use_container_width=True):
            export_review(review_result, "latex")
    with col5:
        if st.button("Start New", use_container_width=True):
            st.session_state.generated_review = None
            st.rerun()
    
    st.divider()
    
    # Review preview
    st.header("Review Preview")
    
    st.markdown('<div class="review-preview">', unsafe_allow_html=True)
    st.markdown(review_result['content'])
    st.markdown('</div>', unsafe_allow_html=True)


def export_review(review_result, format_type):
    """Export the review in specified format"""
    try:
        if format_type == "markdown":
            content = review_result['markdown_content']
            st.download_button(
                "📥 Download Markdown",
                content,
                file_name="literature_review.md",
                mime="text/markdown"
            )
        
        elif format_type == "latex":
            content = review_result['latex_content']
            st.download_button(
                "📥 Download LaTeX",
                content,
                file_name="literature_review.tex",
                mime="text/plain"
            )
        
        elif format_type == "word":
            doc = lit_review_agent.export_review(
                review_result['content'],
                format="word"
            )
            st.download_button(
                "📥 Download Word",
                doc,
                file_name="literature_review.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        elif format_type == "pdf":
            pdf = lit_review_agent.export_review(
                review_result['content'],
                format="pdf"
            )
            st.download_button(
                "📥 Download PDF",
                pdf,
                file_name="literature_review.pdf",
                mime="application/pdf"
            )
        
        st.success("Export ready!")
    
    except Exception as e:
        st.error(f"Export failed: {str(e)}")
        logger.error(f"Review export error: {str(e)}")


if __name__ == "__main__":
    main()
