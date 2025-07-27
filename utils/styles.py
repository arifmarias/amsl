# utils/styles.py

from utils.theme import ModernTheme

# In utils/styles.py, update the get_modern_css() function by adding these sidebar styles:

def get_modern_css():
    """Get the complete modern CSS styling"""
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Main App Container */
        .stApp {{
            background-color: {ModernTheme.BACKGROUND};
        }}
        
        /* Modern Header */
        .modern-header {{
            background: linear-gradient(135deg, {ModernTheme.PRIMARY} 0%, {ModernTheme.PRIMARY_DARK} 100%);
            color: white;
            padding: 2rem;
            border-radius: {ModernTheme.RADIUS_XL};
            margin-bottom: 2rem;
            box-shadow: {ModernTheme.SHADOW_LG};
        }}
        
        .modern-header h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin: 0;
            letter-spacing: -0.025em;
        }}
        
        .modern-header p {{
            font-size: 1rem;
            opacity: 0.9;
            margin: 0.5rem 0 0 0;
        }}
        
        /* Sidebar Subtle Improvements */
        section[data-testid="stSidebar"] > div {{
            background-color: {ModernTheme.SURFACE};
            padding-top: 1rem;
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: white;
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {ModernTheme.ACCENT};
            color: white;
            border-color: {ModernTheme.ACCENT};
            transform: translateX(2px);
        }}
        
        /* Card Styles */
        .modern-card {{
            background-color: {ModernTheme.SURFACE};
            padding: 1.5rem;
            border-radius: {ModernTheme.RADIUS_LG};
            border: 1px solid {ModernTheme.BORDER};
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        
        .modern-card:hover {{
            box-shadow: {ModernTheme.SHADOW_MD};
            transform: translateY(-2px);
        }}
        
        /* Metric Cards */
        [data-testid="metric-container"] {{
            background: white;
            padding: 1.25rem;
            border-radius: {ModernTheme.RADIUS_LG};
            border: 1px solid {ModernTheme.BORDER};
            box-shadow: {ModernTheme.SHADOW_SM};
            transition: all 0.3s ease;
        }}
        
        [data-testid="metric-container"]:hover {{
            box-shadow: {ModernTheme.SHADOW_MD};
            border-color: {ModernTheme.ACCENT}40;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-label"] {{
            font-size: 0.875rem;
            color: {ModernTheme.TEXT_SECONDARY};
            font-weight: 500;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            font-size: 1.875rem;
            font-weight: 700;
            color: {ModernTheme.TEXT_PRIMARY};
        }}
        
        [data-testid="metric-container"] [data-testid="metric-delta"] {{
            font-size: 0.75rem;
        }}
        
        /* Button Styles */
        .stButton > button {{
            background-color: {ModernTheme.ACCENT};
            color: white;
            border: none;
            padding: 0.625rem 1.25rem;
            font-size: 0.875rem;
            font-weight: 500;
            border-radius: {ModernTheme.RADIUS_MD};
            transition: all 0.2s ease;
            box-shadow: {ModernTheme.SHADOW_SM};
        }}
        
        .stButton > button:hover {{
            background-color: {ModernTheme.ACCENT_HOVER};
            box-shadow: {ModernTheme.SHADOW_MD};
            transform: translateY(-1px);
        }}
        
        /* Secondary Button Style */
        .secondary-button > button {{
            background-color: {ModernTheme.SURFACE};
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
        }}
        
        .secondary-button > button:hover {{
            background-color: {ModernTheme.BORDER};
            border-color: {ModernTheme.TEXT_SECONDARY};
        }}
        
        /* Form Styles */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {{
            border: 1px solid {ModernTheme.BORDER};
            border-radius: {ModernTheme.RADIUS_MD};
            padding: 0.625rem 0.875rem;
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }}
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {ModernTheme.ACCENT};
            box-shadow: 0 0 0 3px {ModernTheme.ACCENT_LIGHT};
        }}
        
        /* Tab Styles */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background-color: {ModernTheme.SURFACE};
            padding: 0.5rem;
            border-radius: {ModernTheme.RADIUS_LG};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 2.5rem;
            padding: 0 1.5rem;
            background-color: transparent;
            border-radius: {ModernTheme.RADIUS_MD};
            color: {ModernTheme.TEXT_SECONDARY};
            font-weight: 500;
            font-size: 0.875rem;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {ModernTheme.BACKGROUND};
            color: {ModernTheme.TEXT_PRIMARY};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: white !important;
            color: {ModernTheme.ACCENT} !important;
            box-shadow: {ModernTheme.SHADOW_SM};
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status-new {{
            background-color: {ModernTheme.INFO}20;
            color: {ModernTheme.INFO};
        }}
        
        .status-active {{
            background-color: {ModernTheme.SUCCESS}20;
            color: {ModernTheme.SUCCESS};
        }}
        
        .status-completed {{
            background-color: {ModernTheme.ACCENT}20;
            color: {ModernTheme.ACCENT};
        }}
        
        .status-on-hold {{
            background-color: {ModernTheme.WARNING}20;
            color: {ModernTheme.WARNING};
        }}
        
        .status-cancelled {{
            background-color: {ModernTheme.ERROR}20;
            color: {ModernTheme.ERROR};
        }}
        
        /* Info Box Styles */
        .info-box {{
            background-color: {ModernTheme.ACCENT_LIGHT};
            border: 1px solid {ModernTheme.ACCENT}40;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1rem;
            border-radius: {ModernTheme.RADIUS_MD};
            margin: 1rem 0;
        }}
        
        .success-box {{
            background-color: {ModernTheme.SUCCESS}10;
            border: 1px solid {ModernTheme.SUCCESS}30;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1rem;
            border-radius: {ModernTheme.RADIUS_MD};
            margin: 1rem 0;
        }}
        
        .warning-box {{
            background-color: {ModernTheme.WARNING}10;
            border: 1px solid {ModernTheme.WARNING}30;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1rem;
            border-radius: {ModernTheme.RADIUS_MD};
            margin: 1rem 0;
        }}
        
        .error-box {{
            background-color: {ModernTheme.ERROR}10;
            border: 1px solid {ModernTheme.ERROR}30;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1rem;
            border-radius: {ModernTheme.RADIUS_MD};
            margin: 1rem 0;
        }}
        
        /* Modern Table Styles */
        .dataframe {{
            border: none !important;
            font-size: 0.875rem;
        }}
        
        .dataframe thead tr th {{
            background-color: {ModernTheme.SURFACE} !important;
            color: {ModernTheme.TEXT_PRIMARY} !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            padding: 0.75rem 1rem !important;
            border-bottom: 2px solid {ModernTheme.BORDER} !important;
        }}
        
        .dataframe tbody tr {{
            border-bottom: 1px solid {ModernTheme.BORDER} !important;
        }}
        
        .dataframe tbody tr:hover {{
            background-color: {ModernTheme.SURFACE} !important;
        }}
        
        .dataframe tbody tr td {{
            padding: 0.75rem 1rem !important;
            color: {ModernTheme.TEXT_PRIMARY} !important;
        }}
        
        /* Plotly Chart Container */
        .js-plotly-plot {{
            border-radius: {ModernTheme.RADIUS_LG};
            border: 1px solid {ModernTheme.BORDER};
            padding: 1rem;
            background: white;
            box-shadow: {ModernTheme.SHADOW_SM};
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {ModernTheme.SURFACE};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {ModernTheme.BORDER};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {ModernTheme.TEXT_SECONDARY};
        }}
    </style>
    """
