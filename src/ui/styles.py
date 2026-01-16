import streamlit as st

def load_css():
    """Injects custom CSS for a premium, modern B2B application look."""
    st.markdown("""
        <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* GLOBAL RESET & TYPOGRAPHY */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
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

        /* CARD UI COMPONENT */
        .css-card {
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid rgba(128, 128, 128, 0.2);
            margin-bottom: 20px;
        }
        
        /* CUSTOM METRIC BOXES */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-color: var(--primary-color);
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

        /* BUTTONS */
        button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, #1d4ed8 100%);
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            transition: all 0.2s;
        }
        button[kind="primary"]:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            transform: translateY(-1px);
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
            background-image: linear-gradient(90deg, var(--primary-color), #60a5fa);
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

