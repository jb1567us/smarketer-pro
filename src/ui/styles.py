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
            max_width: 1200px;
        }

        /* CARD UI COMPONENT */
        .css-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #f0f2f6;
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
            border-color: rgba(128, 128, 128, 0.4);
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
            /* background-color: #f8f9fa; REMOVED to allow default dark theme */
            border-right: 1px solid #374151;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 3rem;
        }

        /* BUTTONS */
        button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
            transition: all 0.2s;
        }
        button[kind="primary"]:hover {
            box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
            transform: translateY(-1px);
        }
        button[kind="secondary"] {
            background-color: white;
            border: 1px solid #d1d5db;
            color: #374151;
            border-radius: 8px;
        }

        /* INPUT FIELDS */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            border-radius: 8px;
            border-color: #d1d5db;
        }
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
            border-color: #2563eb;
            box-shadow: 0 0 0 1px #2563eb;
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            color: #4b5563;
            font-weight: 500;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #2563eb;
            border-bottom: 2px solid #2563eb;
            margin-bottom: -2px; 
            font-weight: 700;
        }

        /* HEADERS */
        h1 {
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #111827;
        }
        h2, h3 {
            font-weight: 700;
            letter-spacing: -0.01em;
            color: #1f2937;
        }
        
        /* EXPANDERS */
        .streamlit-expanderHeader {
            background-color: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            color: #111827;
            font-weight: 600;
        }
        
        /* PROGRESS BAR */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #2563eb, #60a5fa);
        }

        </style>
    """, unsafe_allow_html=True)
