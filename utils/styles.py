# utils/styles.py - Fixed Text Visibility CSS

from utils.theme import ModernTheme

def get_modern_css():
    """Get the complete enhanced modern CSS styling with proper text visibility"""
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* CSS Variables for consistent theming */
        :root {{
            --primary: {ModernTheme.PRIMARY};
            --primary-light: {ModernTheme.PRIMARY_LIGHT};
            --primary-hover: {ModernTheme.PRIMARY_HOVER};
            --accent: {ModernTheme.ACCENT};
            --accent-hover: {ModernTheme.ACCENT_HOVER};
            --accent-light: {ModernTheme.ACCENT_LIGHT};
            --background: {ModernTheme.BACKGROUND};
            --surface: {ModernTheme.SURFACE};
            --border: {ModernTheme.BORDER};
            --text-primary: {ModernTheme.TEXT_PRIMARY};
            --text-secondary: {ModernTheme.TEXT_SECONDARY};
            --success: {ModernTheme.SUCCESS};
            --warning: {ModernTheme.WARNING};
            --error: {ModernTheme.ERROR};
            --shadow-sm: {ModernTheme.SHADOW_SM};
            --shadow-md: {ModernTheme.SHADOW_MD};
            --shadow-lg: {ModernTheme.SHADOW_LG};
            --radius-md: {ModernTheme.RADIUS_MD};
            --radius-lg: {ModernTheme.RADIUS_LG};
            --radius-xl: {ModernTheme.RADIUS_XL};
            --transition: {ModernTheme.TRANSITION_NORMAL};
        }}
        
        /* Global Styles - FIXED TEXT COLORS */
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }}
        
        /* Main App Container */
        .stApp {{
            background-color: var(--background);
            color: var(--text-primary) !important;
        }}
        
        /* Fix all text elements to be dark */
        .stApp p, .stApp div, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: var(--text-primary) !important;
        }}
        
        /* Fix form labels */
        .stTextInput > label, .stSelectbox > label, .stTextArea > label, .stNumberInput > label, .stRadio > label {{
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }}
        
        /* Fix markdown text */
        .stMarkdown {{
            color: var(--text-primary) !important;
        }}
        
        /* Fix info, success, warning, error text */
        .stAlert > div {{
            color: var(--text-primary) !important;
        }}
        
        /* Enhanced Header - LIGHTER BACKGROUND */
        .modern-header {{
            background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
            color: {ModernTheme.TEXT_WHITE} !important;
            padding: 2.5rem;
            border-radius: var(--radius-xl);
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
        }}
        
        .modern-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.15) 0%, transparent 50%);
            pointer-events: none;
        }}
        
        .modern-header h1, .modern-header p {{
            color: {ModernTheme.TEXT_WHITE} !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }}
        
        .modern-header h1 {{
            font-size: {ModernTheme.FONT_SIZES['3xl']};
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.025em;
            position: relative;
            z-index: 1;
        }}
        
        .modern-header p {{
            font-size: {ModernTheme.FONT_SIZES['lg']};
            opacity: 0.95;
            margin: 0.75rem 0 0 0;
            position: relative;
            z-index: 1;
            font-weight: 400;
        }}
        
        /* Enhanced Sidebar - FIXED BUTTON TEXT */
        section[data-testid="stSidebar"] > div {{
            background-color: var(--surface);
            padding-top: 1.5rem;
            border-right: 1px solid var(--border);
        }}
        
        /* Fix sidebar text */
        section[data-testid="stSidebar"] * {{
            color: var(--text-primary) !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: var(--accent) !important;
            color: {ModernTheme.TEXT_WHITE} !important;
            border: 1px solid var(--accent);
            font-weight: 600 !important;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            padding: 0.75rem 1rem;
            border-radius: var(--radius-md);
            transition: all var(--transition);
            width: 100%;
            margin-bottom: 0.5rem;
            box-shadow: var(--shadow-sm);
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: var(--accent-hover) !important;
            color: {ModernTheme.TEXT_WHITE} !important;
            border-color: var(--accent-hover);
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }}
        
        /* Specific fix for active/selected sidebar buttons */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background-color: var(--accent) !important;
            color: {ModernTheme.TEXT_WHITE} !important;
            font-weight: 700 !important;
        }}
        
        /* Enhanced Metric Cards - FIXED TEXT */
        [data-testid="metric-container"] {{
            background: {ModernTheme.TEXT_WHITE};
            padding: 1.5rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            transition: all var(--transition);
            position: relative;
            overflow: hidden;
        }}
        
        [data-testid="metric-container"] * {{
            color: var(--text-primary) !important;
        }}
        
        [data-testid="metric-container"]:hover {{
            box-shadow: var(--shadow-md);
            border-color: var(--accent-light);
            transform: translateY(-1px);
        }}
        
        [data-testid="metric-container"] [data-testid="metric-label"] {{
            font-size: {ModernTheme.FONT_SIZES['sm']};
            color: var(--text-secondary) !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            font-size: {ModernTheme.FONT_SIZES['2xl']};
            font-weight: 700;
            color: var(--text-primary) !important;
            line-height: 1.2;
        }}
        
        /* Enhanced Button Styles */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
            color: {ModernTheme.TEXT_WHITE} !important;
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            font-weight: 600;
            border-radius: var(--radius-md);
            transition: all var(--transition);
            box-shadow: var(--shadow-sm);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        /* Enhanced Form Styles - FIXED TEXT */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.75rem 1rem;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            transition: all var(--transition);
            background-color: {ModernTheme.TEXT_WHITE};
            color: var(--text-primary) !important;
            font-weight: 400;
        }}
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus,
        .stNumberInput > div > div > input:focus {{
            border-color: var(--accent);
            box-shadow: {ModernTheme.FOCUS_RING};
            outline: none;
        }}
        
        /* Enhanced Tab Styles - FIXED TEXT */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.25rem;
            background-color: var(--surface);
            padding: 0.25rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 2.75rem;
            padding: 0 1.5rem;
            background-color: transparent;
            border-radius: var(--radius-md);
            color: var(--text-secondary) !important;
            font-weight: 500;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            transition: all var(--transition);
            border: none;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {ModernTheme.HOVER_OVERLAY};
            color: var(--text-primary) !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%) !important;
            color: {ModernTheme.TEXT_WHITE} !important;
            box-shadow: var(--shadow-sm);
            font-weight: 600;
        }}
        
        /* Enhanced Table Styles - FIXED TEXT */
        .dataframe {{
            border: none !important;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}
        
        .dataframe * {{
            color: var(--text-primary) !important;
        }}
        
        .dataframe thead tr th {{
            background: linear-gradient(135deg, var(--surface) 0%, {ModernTheme.BACKGROUND_ALT} 100%) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: {ModernTheme.FONT_SIZES['xs']};
            letter-spacing: 0.05em;
            padding: 1rem !important;
            border-bottom: 2px solid var(--border) !important;
            border-right: 1px solid var(--border) !important;
        }}
        
        .dataframe tbody tr {{
            border-bottom: 1px solid var(--border) !important;
            transition: all var(--transition);
        }}
        
        .dataframe tbody tr:hover {{
            background-color: {ModernTheme.BACKGROUND_ALT} !important;
        }}
        
        .dataframe tbody tr td {{
            padding: 0.875rem 1rem !important;
            color: var(--text-primary) !important;
            border-right: 1px solid var(--border) !important;
        }}
        
        /* Fix radio button labels */
        .stRadio > div > label > div {{
            color: var(--text-primary) !important;
        }}
        
        /* Fix selectbox options */
        .stSelectbox > div > div > div {{
            color: var(--text-primary) !important;
        }}
        
        /* Fix checkbox labels */
        .stCheckbox > label > div {{
            color: var(--text-primary) !important;
        }}
        
        /* Fix file uploader text */
        .stFileUploader > div > div > div {{
            color: var(--text-secondary) !important;
        }}
        
        /* Fix expander headers */
        .streamlit-expanderHeader {{
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem;
            font-weight: 600;
            color: var(--text-primary) !important;
            transition: all var(--transition);
        }}
        
        /* Success/Error Message Styling - FIXED TEXT */
        .stSuccess {{
            background-color: {ModernTheme.SUCCESS_BG};
            border: 1px solid {ModernTheme.SUCCESS_BORDER};
            border-left: 4px solid {ModernTheme.SUCCESS};
            border-radius: var(--radius-md);
            padding: 1rem;
            color: var(--text-primary) !important;
        }}
        
        .stSuccess * {{
            color: var(--text-primary) !important;
        }}
        
        .stError {{
            background-color: {ModernTheme.ERROR_BG};
            border: 1px solid {ModernTheme.ERROR_BORDER};
            border-left: 4px solid {ModernTheme.ERROR};
            border-radius: var(--radius-md);
            padding: 1rem;
            color: var(--text-primary) !important;
        }}
        
        .stError * {{
            color: var(--text-primary) !important;
        }}
        
        .stWarning {{
            background-color: {ModernTheme.WARNING_BG};
            border: 1px solid {ModernTheme.WARNING_BORDER};
            border-left: 4px solid {ModernTheme.WARNING};
            border-radius: var(--radius-md);
            padding: 1rem;
            color: var(--text-primary) !important;
        }}
        
        .stWarning * {{
            color: var(--text-primary) !important;
        }}
        
        .stInfo {{
            background-color: {ModernTheme.INFO_BG};
            border: 1px solid {ModernTheme.INFO_BORDER};
            border-left: 4px solid {ModernTheme.INFO};
            border-radius: var(--radius-md);
            padding: 1rem;
            color: var(--text-primary) !important;
        }}
        
        .stInfo * {{
            color: var(--text-primary) !important;
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
            background: var(--surface);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
            transition: all var(--transition);
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-secondary);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .modern-header {{
                padding: 1.5rem;
                margin-bottom: 1rem;
            }}
            
            .modern-header h1 {{
                font-size: {ModernTheme.FONT_SIZES['2xl']};
            }}
        }}
    </style>
    """