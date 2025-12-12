import streamlit as st
from datetime import datetime
from database.database import db
from agents.export_agent import export_agent
from utils.error_handler import logger
import sys
sys.path.append('..')
from components.navbar import render_navbar
from components.footer import render_footer

st.set_page_config(page_title="Projects", page_icon=None, layout="wide")

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
    .project-card {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .project-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .tag-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        background-color: #e3f2fd;
        color: #1976d2;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .paper-mini-card {
        background-color: var(--secondary-background-color);
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None
if 'show_create_form' not in st.session_state:
    st.session_state.show_create_form = False


def main():
    render_navbar(current_page="Projects")
    
    st.title("Research Projects")
    st.markdown("Organize and manage your research papers")
    
    # Sidebar
    with st.sidebar:
        st.header("Projects Overview")
        
        try:
            stats = db.get_statistics()
            st.metric("Total Projects", stats.get('total_projects', 0))
            st.metric("Total Papers", stats.get('total_papers', 0))
            st.metric("Papers with PDFs", stats.get('papers_with_pdf', 0))
        except:
            st.info("No statistics available")
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("New Project", use_container_width=True):
            st.session_state.show_create_form = True
            st.session_state.selected_project = None
            st.rerun()
        
        if st.button("Search Papers", use_container_width=True):
            st.switch_page("pages/Search.py")
        
        if st.button("Generate Review", use_container_width=True):
            st.switch_page("pages/Literature_Review.py")
    
    # Main content
    if st.session_state.show_create_form:
        show_create_project_form()
    elif st.session_state.selected_project:
        show_project_details()
    else:
        show_projects_list()
    
    # Render footer
    render_footer()


def show_create_project_form():
    """Display form to create a new project"""
    st.header("Create New Project")
    
    with st.form("create_project_form"):
        name = st.text_input("Project Name*", placeholder="e.g., PhD Literature Review")
        description = st.text_area("Description", placeholder="Brief description of your research project...")
        
        # Tags input
        tags_input = st.text_input("Tags (comma-separated)", placeholder="machine learning, healthcare, deep learning")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Project", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if submit:
            if not name:
                st.error("Project name is required")
            else:
                try:
                    project = db.create_project(name=name, description=description, tags=tags)
                    if project:
                        st.success(f"Project '{name}' created successfully!")
                        st.session_state.show_create_form = False
                        st.session_state.selected_project = project.id
                        st.rerun()
                    else:
                        st.error("Failed to create project")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if cancel:
            st.session_state.show_create_form = False
            st.rerun()


def show_projects_list():
    """Display list of all projects"""
    st.header("Your Projects")
    
    try:
        projects = db.get_all_projects()
        
        if not projects:
            st.info("No projects yet. Create your first project to get started!")
            if st.button("Create First Project"):
                st.session_state.show_create_form = True
                st.rerun()
            return
        
        # Search/filter bar
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Search projects", placeholder="Search by name or tags...", label_visibility="collapsed")
        with col2:
            sort_by = st.selectbox("Sort by", ["Recent", "Name", "Papers Count"], label_visibility="collapsed")
        
        # Filter projects
        filtered_projects = projects
        if search_term:
            filtered_projects = [
                p for p in projects 
                if search_term.lower() in p.name.lower() 
                or any(search_term.lower() in tag.lower() for tag in (p.tags or []))
            ]
        
        # Sort projects
        if sort_by == "Recent":
            filtered_projects = sorted(filtered_projects, key=lambda x: x.updated_at, reverse=True)
        elif sort_by == "Name":
            filtered_projects = sorted(filtered_projects, key=lambda x: x.name)
        elif sort_by == "Papers Count":
            # Get paper counts
            filtered_projects = sorted(
                filtered_projects, 
                key=lambda x: len(db.get_project_papers(x.id)), 
                reverse=True
            )
        
        st.markdown(f"**{len(filtered_projects)} project(s)**")
        
        # Display projects as cards
        for project in filtered_projects:
            display_project_card(project)
    
    except Exception as e:
        st.error(f"❌ Error loading projects: {str(e)}")
        logger.error(f"Projects list error: {str(e)}")


def display_project_card(project):
    """Display a project as a card"""
    papers = db.get_project_papers(project.id)
    paper_count = len(papers)
    
    with st.container():
        st.markdown('<div class="project-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### 📁 {project.name}")
            if project.description:
                st.markdown(project.description)
            
            # Tags
            if project.tags:
                tags_html = "".join([f'<span class="tag-badge">{tag}</span>' for tag in project.tags])
                st.markdown(tags_html, unsafe_allow_html=True)
        
        with col2:
            st.metric("Papers", paper_count)
            st.caption(f"Updated: {project.updated_at.strftime('%m/%d/%Y')}")
        
        with col3:
            if st.button("Open →", key=f"open_{project.id}", use_container_width=True):
                st.session_state.selected_project = project.id
                st.rerun()
            
            if st.button("🗑️ Delete", key=f"del_{project.id}", use_container_width=True):
                if st.session_state.get(f'confirm_delete_{project.id}'):
                    db.delete_project(project.id)
                    st.success("Project deleted!")
                    st.rerun()
                else:
                    st.session_state[f'confirm_delete_{project.id}'] = True
                    st.warning("Click again to confirm")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")


def show_project_details():
    """Display detailed view of a project"""
    project_id = st.session_state.selected_project
    
    try:
        project = db.get_project(project_id)
        if not project:
            st.error("Project not found")
            st.session_state.selected_project = None
            return
        
        # Header with back button
        col1, col2 = st.columns([5, 1])
        with col1:
            st.title(f"📁 {project.name}")
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state.selected_project = None
                st.rerun()
        
        if project.description:
            st.markdown(project.description)
        
        # Tags
        if project.tags:
            tags_html = "".join([f'<span class="tag-badge">{tag}</span>' for tag in project.tags])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        st.markdown(f"*Created: {project.created_at.strftime('%B %d, %Y')} | Updated: {project.updated_at.strftime('%B %d, %Y')}*")
        
        st.divider()
        
        # Tabs for different views
        tabs = st.tabs(["Papers", "Notes", "Statistics", "Settings"])
        
        with tabs[0]:  # Papers
            show_project_papers(project)
        
        with tabs[1]:  # Notes
            show_project_notes(project)
        
        with tabs[2]:  # Statistics
            show_project_statistics(project)
        
        with tabs[3]:  # Settings
            show_project_settings(project)
    
    except Exception as e:
        st.error(f"Error loading project: {str(e)}")
        logger.error(f"Project details error: {str(e)}")


def show_project_papers(project):
    """Display papers in a project"""
    papers = db.get_project_papers(project.id)
    
    if not papers:
        st.info("No papers in this project yet. Add papers from the Search page!")
        if st.button("Go to Search"):
            st.switch_page("pages/Search.py")
        return
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        export_format = st.selectbox("Export as", ["Word", "PDF", "CSV", "BibTeX", "Markdown"])
    with col2:
        st.write("")  # Spacing
    with col3:
        if st.button("📥 Export All Papers", use_container_width=True):
            export_project_papers(papers, export_format)
    
    st.markdown(f"**{len(papers)} paper(s) in this project**")
    
    # Display papers
    for i, paper in enumerate(papers, 1):
        with st.container():
            st.markdown('<div class="paper-mini-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{i}. {paper.title}**")
                authors = ", ".join((paper.authors or [])[:3])
                if len(paper.authors or []) > 3:
                    authors += " et al."
                st.caption(f"{authors} • {paper.year} • {paper.citation_count} citations")
            
            with col2:
                if st.button("Remove", key=f"remove_{paper.id}"):
                    db.remove_paper_from_project(project.id, paper.id)
                    st.success("Removed!")
                    st.rerun()
            
            # Show summary if available
            if paper.abstract_summary_medium or paper.abstract:
                with st.expander("View summary"):
                    st.write(paper.abstract_summary_medium or paper.abstract[:300])
            
            st.markdown('</div>', unsafe_allow_html=True)


def show_project_notes(project):
    """Display and manage project notes"""
    st.subheader("Project Notes")
    
    # Add new note
    with st.expander("Add New Note"):
        with st.form("add_note_form"):
            note_title = st.text_input("Note Title")
            note_content = st.text_area("Note Content", height=150)
            note_type = st.selectbox("Note Type", ["general", "literature_review", "methodology", "findings", "ideas"])
            
            if st.form_submit_button("Save Note"):
                if note_content:
                    db.add_project_note(project.id, note_title, note_content, note_type)
                    st.success("Note added!")
                    st.rerun()
    
    # Display existing notes
    notes = db.get_project_notes(project.id)
    
    if notes:
        for note in notes:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{note.title or 'Untitled Note'}**")
                    st.caption(f"{note.note_type} • {note.created_at.strftime('%m/%d/%Y')}")
                with col2:
                    st.caption("")  # Spacing
                
                st.write(note.content)
                st.divider()
    else:
        st.info("No notes yet. Add your first note above!")


def show_project_statistics(project):
    """Display project statistics"""
    papers = db.get_project_papers(project.id)
    
    if not papers:
        st.info("No statistics available yet. Add papers to see analytics.")
        return
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Papers", len(papers))
    
    with col2:
        papers_with_pdf = sum(1 for p in papers if p.has_pdf)
        st.metric("With PDFs", papers_with_pdf)
    
    with col3:
        total_citations = sum(p.citation_count or 0 for p in papers)
        st.metric("Total Citations", total_citations)
    
    with col4:
        years = [p.year for p in papers if p.year and isinstance(p.year, int)]
        avg_year = sum(years) // len(years) if years else 0
        st.metric("Avg Year", avg_year)
    
    st.divider()
    
    # Year distribution
    st.subheader("Year Distribution")
    if years:
        import plotly.express as px
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        fig = px.bar(
            x=list(year_counts.keys()),
            y=list(year_counts.values()),
            labels={'x': 'Year', 'y': 'Number of Papers'},
            title="Papers by Publication Year"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top venues
    st.subheader("Top Venues")
    venues = {}
    for paper in papers:
        if paper.venue:
            venues[paper.venue] = venues.get(paper.venue, 0) + 1
    
    if venues:
        top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:10]
        for venue, count in top_venues:
            st.write(f"• **{venue}**: {count} paper(s)")


def show_project_settings(project):
    """Display project settings"""
    st.subheader("Project Settings")
    
    # Edit project
    with st.form("edit_project_form"):
        new_name = st.text_input("Project Name", value=project.name)
        new_description = st.text_area("Description", value=project.description or "")
        
        current_tags = ", ".join(project.tags) if project.tags else ""
        tags_input = st.text_input("Tags (comma-separated)", value=current_tags)
        new_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        if st.form_submit_button("Save Changes", type="primary"):
            db.update_project(
                project.id,
                name=new_name,
                description=new_description,
                tags=new_tags
            )
            st.success("Project updated!")
            st.rerun()
    
    st.divider()
    
    # Danger zone
    st.subheader("Danger Zone")
    st.warning("These actions cannot be undone!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete Project", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_delete_project'):
                db.delete_project(project.id)
                st.success("Project deleted!")
                st.session_state.selected_project = None
                st.rerun()
            else:
                st.session_state.confirm_delete_project = True
                st.error("Click again to confirm deletion")


def export_project_papers(papers, format_type):
    """Export all papers in project"""
    # Convert database papers to dict format
    papers_dict = []
    for paper in papers:
        paper_dict = {
            'title': paper.title,
            'authors': paper.authors or [],
            'year': paper.year,
            'venue': paper.venue,
            'citation_count': paper.citation_count,
            'abstract': paper.abstract,
            'abstract_summary': paper.abstract_summary_medium,
            'url': paper.url,
            'doi': paper.doi,
            'has_pdf': paper.has_pdf
        }
        papers_dict.append(paper_dict)
    
    try:
        if format_type == "Word":
            doc = export_agent.export_to_word(papers_dict)
            st.download_button(
                "📥 Download",
                doc,
                file_name="project_papers.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        elif format_type == "PDF":
            pdf = export_agent.export_to_pdf(papers_dict)
            st.download_button("📥 Download", pdf, file_name="project_papers.pdf", mime="application/pdf")
        elif format_type == "CSV":
            csv = export_agent.export_to_csv(papers_dict)
            st.download_button("📥 Download", csv.getvalue(), file_name="project_papers.csv", mime="text/csv")
        elif format_type == "BibTeX":
            bib = export_agent.export_to_bibtex(papers_dict)
            st.download_button("📥 Download", bib, file_name="project_papers.bib", mime="text/plain")
        elif format_type == "Markdown":
            md = export_agent.export_to_markdown(papers_dict)
            st.download_button("📥 Download", md, file_name="project_papers.md", mime="text/markdown")
        
        st.success("Exported successfully!")
    except Exception as e:
        st.error(f"Export failed: {str(e)}")


if __name__ == "__main__":
    main()
