"""Professional navbar component for ResearchHub Pro"""
import streamlit as st


def render_navbar(current_page="Home"):
    """
    Render a professional navbar with navigation links
    
    Args:
        current_page: Name of the current page to highlight
    """
    # Get theme colors
    theme = {
        'bg': '#0E1117' if st.session_state.get('dark_mode', True) else '#FFFFFF',
        'secondary_bg': '#1A1D29' if st.session_state.get('dark_mode', True) else '#F9FAFB',
        'text': '#FAFAFA' if st.session_state.get('dark_mode', True) else '#111827',
        'text_secondary': '#B0B3B8' if st.session_state.get('dark_mode', True) else '#6B7280',
        'primary': '#6366F1',
        'primary_hover': '#7C3AED',
        'border': '#2D3139' if st.session_state.get('dark_mode', True) else '#E5E7EB',
    }
    
    st.markdown(f"""
        <style>
        .navbar {{
            background: {theme['secondary_bg']};
            padding: 1rem 2rem;
            border-bottom: 1px solid {theme['border']};
            margin: -1rem -1rem 2rem -1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .navbar-brand {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {theme['primary']}, {theme['primary_hover']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-right: 2rem;
        }}
        
        .navbar-links {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .nav-link {{
            padding: 0.5rem 1rem;
            border-radius: 8px;
            color: {theme['text_secondary']};
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
            cursor: pointer;
        }}
        
        .nav-link:hover {{
            background: {theme['primary']};
            color: white;
        }}
        
        .nav-link.active {{
            background: {theme['primary']};
            color: white;
        }}
        </style>
        
        <div class="navbar">
            <div class="navbar-brand">ResearchHub Pro</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons below navbar
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])
    
    with col1:
        if st.button("Home", key="nav_home", use_container_width=True, 
                    type="primary" if current_page == "Home" else "secondary"):
            st.switch_page("app.py")
    
    with col2:
        if st.button("Search", key="nav_search", use_container_width=True,
                    type="primary" if current_page == "Search" else "secondary"):
            st.switch_page("pages/Search.py")
    
    with col3:
        if st.button("Projects", key="nav_projects", use_container_width=True,
                    type="primary" if current_page == "Projects" else "secondary"):
            st.switch_page("pages/Projects.py")
    
    with col4:
        if st.button("Review", key="nav_review", use_container_width=True,
                    type="primary" if current_page == "Review" else "secondary"):
            st.switch_page("pages/Literature_Review.py")
    
    with col5:
        if st.button("Settings", key="nav_settings", use_container_width=True,
                    type="primary" if current_page == "Settings" else "secondary"):
            st.switch_page("pages/Settings.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
