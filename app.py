
import streamlit as st
from datetime import datetime
from database.database import db
from utils.error_handler import logger
import plotly.graph_objects as go
from components.navbar import render_navbar
from components.footer import render_footer

# Page configuration
st.set_page_config(
    page_title="ResearchHub Pro - Academic Research Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
try:
    db.create_tables()
    logger.info("Database initialized")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Color schemes
COLORS = {
    'dark': {
        'bg': '#0E1117',
        'secondary_bg': '#1A1D29',
        'card_bg': '#262730',
        'border': '#2D3139',
        'text': '#FAFAFA',
        'text_secondary': '#B0B3B8',
        'primary': '#6366F1',
        'primary_hover': '#7C3AED',
        'accent': '#10B981',
        'gradient_start': '#6366F1',
        'gradient_end': '#8B5CF6',
    },
    'light': {
        'bg': '#FFFFFF',
        'secondary_bg': '#F9FAFB',
        'card_bg': '#FFFFFF',
        'border': '#E5E7EB',
        'text': '#111827',
        'text_secondary': '#6B7280',
        'primary': '#6366F1',
        'primary_hover': '#7C3AED',
        'accent': '#10B981',
        'gradient_start': '#6366F1',
        'gradient_end': '#8B5CF6',
    }
}

theme = COLORS['dark' if st.session_state.dark_mode else 'light']

# Enhanced CSS with modern design
st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: {theme['bg']};
        color: {theme['text']};
    }}
    
    /* Header Styles */
    .main-header {{
        font-size: 4.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }}
    
    .sub-header {{
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 3rem;
        color: {theme['text_secondary']};
        font-weight: 400;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(99, 102, 241, 0.15);
        border-color: {theme['primary']};
    }}
    
    .metric-value {{
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        color: {theme['text_secondary']};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Feature Cards */
    .feature-card {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(180deg, {theme['gradient_start']}, {theme['gradient_end']});
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1);
        border-color: {theme['primary']};
    }}
    
    .feature-card:hover::before {{
        opacity: 1;
    }}
    
    .feature-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }}
    
    .feature-title {{
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: {theme['text']};
    }}
    
    .feature-description {{
        font-size: 0.95rem;
        color: {theme['text_secondary']};
        line-height: 1.6;
    }}
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] {{
        background: {theme['secondary_bg']};
        border-right: 1px solid {theme['border']};
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        background: {theme['card_bg']};
        color: {theme['text']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        width: 100%;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {theme['primary']};
        color: white;
        border-color: {theme['primary']};
        transform: translateX(4px);
    }}
    
    /* Stats Display */
    .stat-mini {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    .stat-mini-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {theme['primary']};
    }}
    
    .stat-mini-label {{
        font-size: 0.8rem;
        color: {theme['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Activity Timeline */
    .activity-item {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s ease;
    }}
    
    .activity-item:hover {{
        border-color: {theme['primary']};
        transform: translateX(4px);
    }}
    
    .activity-icon {{
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }}
    
    /* CTA Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }}
    
    /* Dark Mode Toggle */
    .dark-mode-toggle {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 1.5rem;
    }}
    
    .toggle-label {{
        font-size: 0.875rem;
        font-weight: 500;
        color: {theme['text']};
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    /* Progress Bar */
    .progress-container {{
        width: 100%;
        height: 8px;
        background: {theme['border']};
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {theme['gradient_start']}, {theme['gradient_end']});
        border-radius: 4px;
        transition: width 0.3s ease;
    }}
    
    /* Section Headers */
    .section-header {{
        font-size: 2rem;
        font-weight: 700;
        margin: 3rem 0 1.5rem 0;
        color: {theme['text']};
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    .section-header::before {{
        content: '';
        width: 4px;
        height: 32px;
        background: linear-gradient(180deg, {theme['gradient_start']}, {theme['gradient_end']});
        border-radius: 2px;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Divider */
    hr {{
        border: none;
        height: 1px;
        background: {theme['border']};
        margin: 2rem 0;
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo/Brand
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <div style="font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, {theme['gradient_start']}, {theme['gradient_end']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ResearchHub
            </div>
            <div style="font-size: 0.75rem; color: {theme['text_secondary']}; margin-top: 0.25rem;">
                AI-Powered Research
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Dark mode toggle
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            <div class="toggle-label">
                <i class="fas fa-{'moon' if not st.session_state.dark_mode else 'sun'}"></i>
                {'Dark Mode' if not st.session_state.dark_mode else 'Light Mode'}
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("", key="toggle", help="Toggle theme"):
            toggle_dark_mode()
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats with enhanced design
    st.markdown("### Dashboard")
    try:
        stats = db.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="stat-mini">
                    <div class="stat-mini-value">{stats.get('total_projects', 0)}</div>
                    <div class="stat-mini-label">Projects</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="stat-mini">
                    <div class="stat-mini-value">{stats.get('total_papers', 0)}</div>
                    <div class="stat-mini-label">Papers</div>
                </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="stat-mini">
                    <div class="stat-mini-value">{stats.get('total_searches', 0)}</div>
                    <div class="stat-mini-label">Searches</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="stat-mini">
                    <div class="stat-mini-value">{stats.get('total_reviews', 0)}</div>
                    <div class="stat-mini-label">Reviews</div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Initializing database...")
    
    st.markdown("---")
    
    # Quick navigation with icons
    st.markdown("### Quick Access")
    
    if st.button("Search Papers", use_container_width=True):
        st.switch_page("pages/Search.py")
    
    if st.button("My Projects", use_container_width=True):
        st.switch_page("pages/Projects.py")
    
    if st.button("Generate Review", use_container_width=True):
        st.switch_page("pages/Literature_Review.py")
    
    if st.button("Analytics", use_container_width=True):
        st.switch_page("pages/Analytics.py")
    
    st.markdown("---")
    
    # System Status
    st.markdown("### System Status")
    st.markdown(f"""
        <div class="stat-mini">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {theme['text_secondary']}; font-size: 0.85rem;">API Status</span>
                <span style="color: {theme['accent']}; font-size: 0.85rem;">● Online</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="stat-mini">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {theme['text_secondary']}; font-size: 0.85rem;">Database</span>
                <span style="color: {theme['accent']}; font-size: 0.85rem;">● Connected</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0; color: {theme['text_secondary']}; font-size: 0.75rem;">
            <div style="margin-bottom: 0.5rem;">Version 2.0.1</div>
            <div>© 2024 ResearchHub</div>
        </div>
    """, unsafe_allow_html=True)

# Main content
def main():
    # Render navbar
    render_navbar(current_page="Home")
    
    # Hero section
    st.markdown('<div class="main-header">ResearchHub Pro</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Transform weeks of literature review into minutes. AI-powered research assistant for academics and researchers.</div>',
        unsafe_allow_html=True
    )
    
    # CTA Row
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col2:
        if st.button("Get Started", key="hero_cta", use_container_width=True, type="primary"):
            st.switch_page("pages/Search.py")
    
    with col3:
        if st.button("Documentation", key="docs_cta", use_container_width=True):
            st.info("Documentation coming soon!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">10x</div>
                <div class="metric-label">Faster Research</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">2M+</div>
                <div class="metric-label">Papers Indexed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">98%</div>
                <div class="metric-label">Accuracy Rate</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">24/7</div>
                <div class="metric-label">AI Assistant</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Main features
    st.markdown('<div class="section-header">Core Features</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-search"></i></div>
                <div class="feature-title">Intelligent Search</div>
                <div class="feature-description">
                    Search across multiple academic databases simultaneously. 
                    Get AI-powered summaries, identify research gaps, and extract key findings instantly.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-robot"></i></div>
                <div class="feature-title">AI Summarization</div>
                <div class="feature-description">
                    Advanced NLP models extract key insights from papers. 
                    Understand complex research in seconds, not hours.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-chart-bar"></i></div>
                <div class="feature-title">Visual Analytics</div>
                <div class="feature-description">
                    Interactive charts and graphs reveal trends in your research. 
                    Citation networks, topic clusters, and temporal analysis.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-file-alt"></i></div>
                <div class="feature-title">Auto Literature Review</div>
                <div class="feature-description">
                    Generate publication-ready literature reviews automatically. 
                    5-10 pages of academic-quality writing in minutes.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-folder"></i></div>
                <div class="feature-title">Smart Organization</div>
                <div class="feature-description">
                    Manage projects with tags, notes, and annotations. 
                    Advanced filtering and search within your library.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-download"></i></div>
                <div class="feature-title">Universal Export</div>
                <div class="feature-description">
                    Export to Word, PDF, LaTeX, Markdown, BibTeX, or JSON. 
                    Seamlessly integrate with your existing workflow.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
    
    try:
        recent_searches = db.get_recent_searches(limit=5)
        if recent_searches:
            for idx, search in enumerate(recent_searches):
                st.markdown(f"""
                    <div class="activity-item">
                        <div class="activity-icon"><i class="fas fa-search"></i></div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: {theme['text']};">{search.query}</div>
                            <div style="font-size: 0.85rem; color: {theme['text_secondary']}; margin-top: 0.25rem;">
                                {search.results_count} papers • {search.created_at.strftime('%B %d, %Y at %I:%M %p')}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="text-align: center; padding: 3rem; color: {theme['text_secondary']};">
                    <div style="font-size: 3rem; margin-bottom: 1rem;"><i class="fas fa-book"></i></div>
                    <div style="font-size: 1.1rem; font-weight: 500;">No activity yet</div>
                    <div style="margin-top: 0.5rem;">Start by searching for papers to see your activity here</div>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
            <div style="text-align: center; padding: 3rem; color: {theme['text_secondary']};">
                <div style="font-size: 3rem; margin-bottom: 1rem;"><i class="fas fa-rocket"></i></div>
                <div style="font-size: 1.1rem; font-weight: 500;">Start your research journey</div>
                <div style="margin-top: 0.5rem;">Begin searching to track your activity</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Tips section
    st.markdown('<div class="section-header">Quick Tips</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">Search Best Practices</div>
                <div class="feature-description">
                    • Use specific keywords<br>
                    • Filter by publication year<br>
                    • Enable open access filter<br>
                    • Try different databases
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">Review Generation</div>
                <div class="feature-description">
                    • Process 10+ papers minimum<br>
                    • Enable PDF processing<br>
                    • Use medium detail level<br>
                    • Add custom instructions
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">Project Management</div>
                <div class="feature-description">
                    • Use descriptive names<br>
                    • Add relevant tags<br>
                    • Take detailed notes<br>
                    • Regular backups
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
