import streamlit as st
import config
from agents.cache_manager import cache
from database.database import db
from utils.error_handler import logger
import os

st.set_page_config(page_title="Settings", page_icon=None, layout="wide")

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
    .settings-section {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .danger-zone {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("Settings & Configuration")
    st.markdown("Manage your application settings and preferences")
    
    # Tabs for different settings categories
    tabs = st.tabs(["Appearance", "Configuration", "Cache", "Database", "About"])
    
    with tabs[0]:  # Appearance
        show_appearance_settings()
    
    with tabs[1]:  # Configuration
        show_configuration_settings()
    
    with tabs[2]:  # Cache
        show_cache_management()
    
    with tabs[3]:  # Database
        show_database_management()
    
    with tabs[4]:  # About
        show_about_info()


def show_appearance_settings():
    """Appearance and UI settings"""
    st.header("Appearance Settings")
    
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    
    # Dark mode toggle
    st.subheader("Dark Mode")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Toggle between light and dark themes")
    with col2:
        current_mode = "Dark" if st.session_state.get('dark_mode', False) else "Light"
        if st.button(f"Switch to {'Light' if current_mode == 'Dark' else 'Dark'}", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.get('dark_mode', False)
            st.rerun()
    
    st.caption(f"Current mode: **{current_mode}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # UI preferences (for future expansion)
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("UI Preferences")
    st.info("Additional UI customization options coming soon!")
    st.markdown('</div>', unsafe_allow_html=True)


def show_configuration_settings():
    """Application configuration"""
    st.header("Configuration Settings")
    
    # Search defaults
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Search Defaults")
    
    default_limit = st.number_input(
        "Default number of papers",
        min_value=1,
        max_value=config.MAX_PAPER_LIMIT,
        value=config.DEFAULT_PAPER_LIMIT,
        help="Default number of papers to retrieve per search"
    )
    
    default_summary = st.selectbox(
        "Default summary level",
        options=list(config.SUMMARY_LEVELS.keys()),
        index=list(config.SUMMARY_LEVELS.keys()).index(config.DEFAULT_SUMMARY_LEVEL),
        format_func=lambda x: f"{x.title()} - {config.SUMMARY_LEVELS[x]['description']}"
    )
    
    default_pdf_processing = st.checkbox(
        "Process PDFs by default",
        value=True,
        help="Automatically download and analyze PDFs when available"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Literature review defaults
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Literature Review Defaults")
    
    default_review_type = st.selectbox(
        "Default review type",
        options=config.LIT_REVIEW_TYPES,
        index=config.LIT_REVIEW_TYPES.index(config.DEFAULT_LIT_REVIEW_TYPE),
        format_func=lambda x: x.title()
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API configuration
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("API Configuration")
    
    groq_key_status = "Configured" if config.GROQ_API_KEY else "Not configured"
    st.write(f"**Groq API Key:** {groq_key_status}")
    
    semantic_key_status = "Configured" if config.SEMANTIC_SCHOLAR_API_KEY else "Optional (not set)"
    st.write(f"**Semantic Scholar API Key:** {semantic_key_status}")
    
    st.info("API keys are configured in the `.env` file. See documentation for setup instructions.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_cache_management():
    """Cache management interface"""
    st.header("Cache Management")
    
    try:
        cache_stats = cache.get_cache_stats()
        
        # Cache statistics
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Cache Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Topic Searches", cache_stats['topic_cache_files'])
        with col2:
            st.metric("Cached Papers", cache_stats['paper_cache_files'])
        with col3:
            st.metric("Total Size", f"{cache_stats['total_size_mb']:.2f} MB")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cache actions
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Cache Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Clear Expired Cache**")
            st.caption(f"Remove items older than {config.CACHE_EXPIRY_DAYS} days")
            if st.button("Clear Expired", use_container_width=True):
                removed = cache.clear_expired_cache()
                total_removed = sum(removed.values())
                st.success(f"Removed {total_removed} expired items")
                st.rerun()
        
        with col2:
            st.write("**Clear All Cache**")
            st.caption("Remove all cached data")
            if st.button("Clear All", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear_cache'):
                    removed = cache.clear_all_cache()
                    total_removed = sum(removed.values())
                    st.success(f"Cleared {total_removed} items")
                    st.session_state.confirm_clear_cache = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_cache = True
                    st.warning("Click again to confirm")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cache benefits
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Cache Benefits")
        st.markdown("""
        - **Faster searches:** Repeated queries return instantly
        - **Reduced API calls:** Saves rate limits
        - **Lower costs:** Fewer API requests
        - **Offline access:** View cached results without internet
        
        **Best practice:** Clear expired cache periodically to free up space.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading cache statistics: {str(e)}")
        logger.error(f"Cache stats error: {str(e)}")


def show_database_management():
    """Database management interface"""
    st.header("Database Management")
    
    try:
        stats = db.get_statistics()
        
        # Database statistics
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Projects", stats['total_projects'])
        with col2:
            st.metric("Papers", stats['total_papers'])
        with col3:
            st.metric("Searches", stats['total_searches'])
        with col4:
            st.metric("With PDFs", stats['papers_with_pdf'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Database info
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Database Information")
        
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./research_agent.db')
        db_type = "PostgreSQL" if database_url.startswith('postgresql') else "SQLite"
        
        st.write(f"**Type:** {db_type}")
        st.write(f"**Location:** {'Cloud (PostgreSQL)' if db_type == 'PostgreSQL' else 'Local (SQLite)'}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Danger zone
        st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
        st.subheader("Danger Zone")
        st.warning("These actions are irreversible!")
        
        if st.button("Reset Database", type="secondary"):
            st.error("This feature is disabled for safety. To reset the database, delete the database file manually.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading database statistics: {str(e)}")
        logger.error(f"Database stats error: {str(e)}")


def show_about_info():
    """About and system information"""
    st.header("About AI Research Agent")
    
    # Application info
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Application Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Version:** 2.0.0 (Phase 2)")
        st.write("**Release:** December 2024")
        st.write("**License:** MIT (Open Source)")
    
    with col2:
        st.write("**Platform:** Streamlit")
        st.write("**AI Model:** LLaMA 3.1 (via Groq)")
        st.write("**Database:** PostgreSQL/SQLite")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Features
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Search & Analysis:**
        - Multi-database search (Semantic Scholar, ArXiv)
        - AI-powered summaries
        - Research gap identification
        - Key findings extraction
        - Automatic deduplication
        """)
    
    with col2:
        st.markdown("""
        **Organization & Export:**
        - Project management
        - Literature review generator
        - 7 export formats
        - Notes and annotations
        - Search history
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # System requirements
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("System Requirements")
    
    st.markdown("""
    **Minimum:**
    - Python 3.9+
    - 4GB RAM
    - Internet connection
    - Groq API key (free)
    
    **Recommended:**
    - Python 3.11+
    - 8GB RAM
    - Stable internet
    - PostgreSQL database (for production)
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Credits
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Credits & Acknowledgments")
    
    st.markdown("""
    **Built with:**
    - [Streamlit](https://streamlit.io) - Web framework
    - [Groq](https://groq.com) - Fast LLM inference
    - [Semantic Scholar](https://www.semanticscholar.org) - Academic search API
    - [ArXiv](https://arxiv.org) - Preprint repository
    
    **Special thanks to:**
    - The open-source community
    - All contributors and testers
    - Academic researchers worldwide
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Links
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("Useful Links")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Documentation**")
        st.markdown("- [User Guide](#)")
        st.markdown("- [API Docs](#)")
        st.markdown("- [FAQ](#)")
    
    with col2:
        st.markdown("**Community**")
        st.markdown("- [GitHub](#)")
        st.markdown("- [Discord](#)")
        st.markdown("- [Forum](#)")
    
    with col3:
        st.markdown("**Support**")
        st.markdown("- [Report Bug](#)")
        st.markdown("- [Request Feature](#)")
        st.markdown("- [Contact](#)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption("ResearchHub - Making research accessible to everyone")
    st.caption("© 2025 - Open Source Project")


if __name__ == "__main__":
    main()
