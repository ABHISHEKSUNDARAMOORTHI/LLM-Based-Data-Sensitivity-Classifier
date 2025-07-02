# styling.py

import streamlit as st
import pandas as pd # Added this import for DataFrame usage in example

def apply_custom_css():
    """
    Applies custom CSS to the Streamlit application for a polished look.
    Includes styles for both light and dark themes, controlled by session state.
    """
    # Initialize theme in session state if not already set
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark' # Default to dark theme

    # Define common styles for the app
    common_css = """
    <style>
    /* General body and app container styling */
    .stApp {
        font-family: 'Inter', sans-serif; /* Use Inter font */
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Streamlit main content block */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        border-radius: 1rem; /* Rounded corners for content blocks */
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        margin-bottom: 0.5em;
        border-radius: 0.5rem; /* Rounded headers */
    }
    h1 { font-size: 2.5em; text-align: center; }
    h2 { font-size: 2em; }
    h3 { font-size: 1.5em; }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 0.75rem; /* More rounded buttons */
        padding: 0.75rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px); /* Lift effect on hover */
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed;
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    .stFileUploader:hover {
        border-color: var(--primary-color);
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 0.75rem;
        overflow: hidden; /* Ensures rounded corners are visible */
        border: 1px solid;
    }
    .dataframe {
        border-radius: 0.75rem;
    }

    /* Info, Success, Warning, Error boxes */
    div[data-testid="stInfo"], div[data-testid="stSuccess"],
    div[data-testid="stWarning"], div[data-testid="stError"] {
        border-left: 6px solid;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stInfo"] { border-color: #3B82F6; } /* Blue */
    div[data-testid="stSuccess"] { border-color: #22C55E; } /* Green */
    div[data-testid="stWarning"] { border-color: #F59E0B; } /* Amber */
    div[data-testid="stError"] { border-color: #EF4444; } /* Red */

    /* Tabs */
    button[data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        font-weight: 700;
        border-bottom: 3px solid var(--primary-color) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        border: 1px solid;
    }
    .streamlit-expanderHeader:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .streamlit-expanderContent {
        border-radius: 0 0 0.75rem 0.75rem;
        padding: 1rem;
        border: 1px solid;
        border-top: none;
    }

    /* Custom box for AI explanation */
    .ai-explanation-box {
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        line-height: 1.6;
    }

    /* Sticky sidebar (requires specific Streamlit version/structure, might need adjustment) */
    .st-emotion-cache-1ldf2b0 { /* This class targets the sidebar container */
        position: sticky;
        top: 0;
        height: 100vh; /* Make it fill the viewport height */
        overflow-y: auto; /* Enable scrolling if content overflows */
        padding-top: 2rem; /* Adjust padding as needed */
    }
    /* Adjust main content padding if sidebar is sticky */
    .st-emotion-cache-1dp5yy6 { /* This targets the main content div */
        padding-left: 2rem; /* Add padding to prevent content from going under sidebar */
    }
    """

    # Define light theme specific styles
    light_theme_css = """
    <style>
    :root {
        --primary-color: #6366F1; /* Indigo 500 */
        --background-color: #FFFFFF; /* White */
        --secondary-background-color: #F8FAFC; /* Slate 50 */
        --text-color: #1E293B; /* Slate 800 */
        --border-color: #E2E8F0; /* Slate 200 */
        --accent-color: #4F46E5; /* Indigo 600 */
    }
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .st-emotion-cache-vk33gh, .st-emotion-cache-16txt3u { /* Sidebar */
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-right: 1px solid var(--border-color);
    }
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
    }
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
    }
    .stButton > button:hover {
        background-color: var(--accent-color);
    }
    .stFileUploader {
        border-color: var(--border-color);
    }
    .stDataFrame {
        border-color: var(--border-color);
    }
    .dataframe {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    .dataframe th {
        background-color: var(--border-color);
        color: var(--text-color);
    }
    .dataframe td {
        color: var(--text-color);
    }
    button[data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-bottom: 2px solid var(--border-color);
    }
    button[data-baseweb="tab"]:hover {
        background-color: var(--border-color);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    .streamlit-expanderHeader {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-color: var(--border-color);
    }
    .streamlit-expanderContent {
        background-color: var(--background-color);
        border-color: var(--border-color);
    }
    .ai-explanation-box {
        background-color: var(--secondary-background-color);
        border-color: var(--border-color);
        color: var(--text-color);
    }
    /* Specific text colors for info/success/warning/error boxes */
    div[data-testid="stInfo"] { color: #3B82F6; background-color: #E0F2FE; }
    div[data-testid="stSuccess"] { color: #22C55E; background-color: #F0FDF4; }
    div[data-testid="stWarning"] { color: #F59E0B; background-color: #FFFBEB; }
    div[data-testid="stError"] { color: #EF4444; background-color: #FEF2F2; }
    </style>
    """

    # Define dark theme specific styles
    dark_theme_css = """
    <style>
    :root {
        --primary-color: #8B5CF6; /* Violet 500 */
        --background-color: #0F172A; /* Slate 950 */
        --secondary-background-color: #1E293B; /* Slate 800 */
        --text-color: #F8FAFC; /* Slate 50 */
        --border-color: #334155; /* Slate 700 */
        --accent-color: #7C3AED; /* Violet 600 */
    }
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .st-emotion-cache-vk33gh, .st-emotion-cache-16txt3u { /* Sidebar */
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-right: 1px solid var(--border-color);
    }
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
    }
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
    }
    .stButton > button:hover {
        background-color: var(--accent-color);
    }
    .stFileUploader {
        border-color: var(--border-color);
    }
    .stDataFrame {
        border-color: var(--border-color);
    }
    .dataframe {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    .dataframe th {
        background-color: var(--border-color);
        color: var(--text-color);
    }
    .dataframe td {
        color: var(--text-color);
    }
    button[data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-bottom: 2px solid var(--border-color);
    }
    button[data-baseweb="tab"]:hover {
        background-color: var(--border-color);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    .streamlit-expanderHeader {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-color: var(--border-color);
    }
    .streamlit-expanderContent {
        background-color: var(--background-color);
        border-color: var(--border-color);
    }
    .ai-explanation-box {
        background-color: var(--secondary-background-color);
        border-color: var(--border-color);
        color: var(--text-color);
    }
    /* Specific text colors for info/success/warning/error boxes */
    div[data-testid="stInfo"] { color: #93C5FD; background-color: #1E293B; }
    div[data-testid="stSuccess"] { color: #86EFAD; background-color: #1E293B; }
    div[data-testid="stWarning"] { color: #FDE68A; background-color: #1E293B; }
    div[data-testid="stError"] { color: #FCA5A5; background-color: #1E293B; }
    </style>
    """

    # Apply common CSS first
    st.markdown(common_css, unsafe_allow_html=True)

    # Apply theme-specific CSS
    if st.session_state.theme == 'dark':
        st.markdown(dark_theme_css, unsafe_allow_html=True)
    else:
        st.markdown(light_theme_css, unsafe_allow_html=True)

def theme_toggle_button():
    """
    Creates a button in the sidebar to toggle between light and dark themes.
    """
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark' # Default theme

    if st.session_state.theme == 'dark':
        if st.sidebar.button("☀️ Switch to Light Theme"):
            st.session_state.theme = 'light'
            st.rerun() # Rerun to apply new theme
    else:
        if st.sidebar.button("🌙 Switch to Dark Theme"):
            st.session_state.theme = 'dark'
            st.rerun() # Rerun to apply new theme

# Example Usage (for testing this file directly)
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("Styling Test Page")

    apply_custom_css()
    theme_toggle_button()

    st.write("This is a test of the custom styling.")
    st.header("A Header Example")
    st.subheader("A Subheader Example")

    st.button("Test Button")
    st.file_uploader("Test File Uploader", type=["txt"])

    st.info("This is an info message.")
    st.success("This is a success message.")
    st.warning("This is a warning message.")
    st.error("This is an error message.")

    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['A', 'B', 'C']})
    st.dataframe(df)

    tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
    with tab1:
        st.write("Content for Tab 1")
    with tab2:
        st.write("Content for Tab 2")

    with st.expander("Click to expand"):
        st.write("Expander content here.")

    st.markdown('<div class="ai-explanation-box">This is a custom AI explanation box.</div>', unsafe_allow_html=True)
