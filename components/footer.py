"""Professional footer component for ResearchHub Pro"""
import streamlit as st


def render_footer():
    """Render a professional footer with copyright, version, and links"""
    # Get theme colors
    theme = {
        'text_secondary': '#B0B3B8' if st.session_state.get('dark_mode', True) else '#6B7280',
        'border': '#2D3139' if st.session_state.get('dark_mode', True) else '#E5E7EB',
        'primary': '#6366F1',
    }
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <style>
        .footer {{
            border-top: 1px solid {theme['border']};
            padding: 2rem 0 1rem 0;
            margin-top: 3rem;
            color: {theme['text_secondary']};
            font-size: 0.875rem;
        }}
        
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .footer-links {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .footer-link {{
            color: {theme['text_secondary']};
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .footer-link:hover {{
            color: {theme['primary']};
        }}
        
        .footer-bottom {{
            text-align: center;
            padding-top: 1rem;
            border-top: 1px solid {theme['border']};
        }}
        </style>
        
        <div class="footer">
            <div class="footer-content">
                <div>
                    <strong>ResearchHub Pro</strong> v2.0.1<br>
                    AI-Powered Academic Research Assistant
                </div>
                <div class="footer-links">
                    <a href="#" class="footer-link">Documentation</a>
                    <a href="#" class="footer-link">Support</a>
                    <a href="#" class="footer-link">Privacy Policy</a>
                    <a href="#" class="footer-link">Terms of Service</a>
                </div>
            </div>
            <div class="footer-bottom">
                © 2025 ResearchHub. All rights reserved.
            </div>
        </div>
    """, unsafe_allow_html=True)
