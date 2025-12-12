# Component Usage Guide

## Overview
This guide shows how to use the professional navbar and footer components in ResearchHub Pro pages.

## Navbar Component

### Import
```python
import sys
sys.path.append('..')
from components.navbar import render_navbar
```

### Usage
```python
def main():
    # Render navbar at the top of your page
    render_navbar(current_page="PageName")
    
    # Your page content here
    st.title("Page Title")
    # ... rest of your code
```

### Parameters
- `current_page` (string): Name of the current page for highlighting
  - Options: "Home", "Search", "Projects", "Review", "Settings"

### Features
- Automatically highlights the active page button
- Responsive button layout
- Theme-aware (adapts to dark/light mode)
- Professional gradient branding
- Navigation to all main pages

## Footer Component

### Import
```python
import sys
sys.path.append('..')
from components.footer import render_footer
```

### Usage
```python
def main():
    # Your page content here
    st.title("Page Title")
    # ... your code
    
    # Render footer at the bottom of your page
    render_footer()
```

### Features
- Copyright information
- Version number (v2.0.1)
- Useful links (Documentation, Support, Privacy Policy, Terms of Service)
- Theme-aware styling
- Consistent spacing

## Complete Example

```python
import streamlit as st
import sys
sys.path.append('..')
from components.navbar import render_navbar
from components.footer import render_footer

st.set_page_config(page_title="My Page", page_icon=None, layout="wide")

def main():
    # 1. Render navbar first
    render_navbar(current_page="MyPage")
    
    # 2. Your page content
    st.title("My Page Title")
    st.markdown("Page description here")
    
    # Your main content...
    col1, col2 = st.columns(2)
    with col1:
        st.write("Content")
    with col2:
        st.write("More content")
    
    # 3. Render footer last
    render_footer()

if __name__ == "__main__":
    main()
```

## Styling Integration

Both components automatically integrate with the application's theme system:

### Dark Mode
- Reads `st.session_state.dark_mode` to determine theme
- Applies appropriate colors automatically

### Color Scheme
- Primary: Indigo (#6366F1)
- Gradient: Indigo to Purple (#8B5CF6)
- Background: Adapts to theme
- Text: Adapts to theme

## Best Practices

### 1. Always Include Both Components
Every page should have both navbar and footer:
```python
def main():
    render_navbar(current_page="PageName")
    # page content
    render_footer()
```

### 2. Correct Page Name
Use the exact page name for proper highlighting:
- Home page: `render_navbar(current_page="Home")`
- Search page: `render_navbar(current_page="Search")`
- Projects page: `render_navbar(current_page="Projects")`
- Review page: `render_navbar(current_page="Review")`
- Settings page: `render_navbar(current_page="Settings")`

### 3. Import Path
Pages in the `pages/` directory need to add parent to path:
```python
import sys
sys.path.append('..')
```

### 4. Page Icon
Set page_icon to None to avoid emoji icons:
```python
st.set_page_config(page_title="...", page_icon=None, layout="wide")
```

## Troubleshooting

### Import Error
If you get `ModuleNotFoundError: No module named 'components'`:
- Ensure `sys.path.append('..')` is called before import
- Verify you're in the pages/ directory structure

### Navbar Not Highlighting
If the active page isn't highlighted:
- Check that `current_page` parameter matches exactly
- Verify it's one of: "Home", "Search", "Projects", "Review", "Settings"

### Styling Issues
If styling looks wrong:
- Ensure Font Awesome CDN is loaded in your page's CSS
- Check that session state is properly initialized
- Verify theme colors are defined

## Component Files

- **Location**: `/components/`
- **Files**:
  - `__init__.py` - Package initialization
  - `navbar.py` - Navbar component (104 lines)
  - `footer.py` - Footer component (75 lines)

## Updates

When updating components:
1. Edit the component file directly
2. Changes apply to all pages automatically
3. Test on all pages to ensure consistency
4. Update this guide if API changes

## Version History

- **v2.0.1** - Initial component creation
  - Professional navbar with active states
  - Standardized footer with links
  - Theme-aware styling
  - Responsive design
