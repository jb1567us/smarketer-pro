import streamlit as st

def load_css():
    """Injects custom CSS for a premium, modern B2B application look."""
    st.markdown("""
        <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* GLOBAL RESET & TYPOGRAPHY */
        html, body, [class*="css"]  {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
            background-color: #F8FAFC; /* Pro Max Background */
        }
        
        /* HIDE DEFAULT STREAMLIT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* MAIN CONTAINER */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 1400px;
        }

        /* CARD UI COMPONENT (Glassmorphism) */
        .css-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(15, 23, 42, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 24px;
            transition: all 0.3s ease;
        }
        .css-card:hover {
            box-shadow: 0 12px 48px 0 rgba(15, 23, 42, 0.1);
            border-color: rgba(15, 23, 42, 0.1);
        }
        
        /* CUSTOM METRIC BOXES (Pro Max Styling) */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(15, 23, 42, 0.1);
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1);
            border-color: #0369A1; /* CTA Trust Blue */
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.8;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-color);
        }

        /* SIDEBAR STYLING */
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 3rem;
        }

        /* BUTTONS (Pro Max Palette) */
        button[kind="primary"] {
            background: linear-gradient(135deg, #0F172A 0%, #0369A1 100%);
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.2);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        button[kind="primary"]:hover {
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.3);
            transform: translateY(-2px);
            filter: brightness(1.1);
        }
        button[kind="secondary"] {
            background-color: transparent;
            border: 1px solid rgba(128, 128, 128, 0.4);
            color: var(--text-color);
            border-radius: 8px;
        }

        /* INPUT FIELDS */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            border-radius: 8px;
            border-color: rgba(128, 128, 128, 0.2);
        }
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 1px var(--primary-color);
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            border-bottom: 2px solid rgba(128, 128, 128, 0.2);
            padding-bottom: 0px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            color: var(--text-color);
            opacity: 0.7;
            font-weight: 500;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: -2px; 
            font-weight: 700;
            opacity: 1;
        }

        /* HEADERS */
        h1, h2, h3 {
            color: var(--text-color);
            letter-spacing: -0.01em;
        }
        h1 { font-weight: 800; }
        h2, h3 { font-weight: 700; }
        
        /* EXPANDERS */
        .streamlit-expanderHeader {
            background-color: var(--secondary-background-color);
            border-radius: 8px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            color: var(--text-color);
            font-weight: 600;
        }
        
        /* PROGRESS BAR */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #0F172A, #0369A1);
            border-radius: 10px;
        }

        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        /* Fix Chat Message Overflow */
        .stChatMessage .stMarkdown {
            word-wrap: break-word !important;
            white-space: pre-wrap !important; 
            overflow-wrap: break-word !important;
            max-width: 100%;
        }
        .stChatMessage code {
            white-space: pre-wrap !important;
            word-break: break-all !important;
        }
        
        /* Ensure dialogs/expanders don't overflow */
        .streamlit-expanderContent {
            overflow-x: auto;
        }
        </style>
    """, unsafe_allow_html=True)

