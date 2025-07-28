# utils/styles.py - Enhanced Modern CSS System

from utils.theme import ModernTheme

def get_modern_css():
    """Get the complete enhanced modern CSS styling"""
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
        
        /* Global Styles */
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        /* Main App Container */
        .stApp {{
            background-color: var(--background);
        }}
        
        /* Enhanced Header */
        .modern-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: {ModernTheme.TEXT_WHITE};
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
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
            pointer-events: none;
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
            opacity: 0.9;
            margin: 0.75rem 0 0 0;
            position: relative;
            z-index: 1;
            font-weight: 400;
        }}
        
        /* Enhanced Sidebar */
        section[data-testid="stSidebar"] > div {{
            background-color: var(--surface);
            padding-top: 1.5rem;
            border-right: 1px solid var(--border);
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {ModernTheme.TEXT_WHITE};
            color: var(--text-primary);
            border: 1px solid var(--border);
            font-weight: 500;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            padding: 0.75rem 1rem;
            border-radius: var(--radius-md);
            transition: all var(--transition);
            width: 100%;
            margin-bottom: 0.5rem;
            box-shadow: var(--shadow-sm);
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: var(--accent);
            color: {ModernTheme.TEXT_WHITE};
            border-color: var(--accent);
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }}
        
        section[data-testid="stSidebar"] .stButton > button[data-selected="true"] {{
            background-color: var(--accent);
            color: {ModernTheme.TEXT_WHITE};
            border-color: var(--accent);
        }}
        
        /* Enhanced Cards */
        .modern-card {{
            background-color: var(--surface);
            padding: 2rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            margin-bottom: 1.5rem;
            transition: all var(--transition);
            box-shadow: var(--shadow-sm);
        }}
        
        .modern-card:hover {{
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
            border-color: var(--accent-light);
        }}
        
        /* Enhanced Metric Cards */
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
        
        [data-testid="metric-container"]:hover {{
            box-shadow: var(--shadow-md);
            border-color: var(--accent-light);
            transform: translateY(-1px);
        }}
        
        [data-testid="metric-container"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent-hover));
        }}
        
        [data-testid="metric-container"] [data-testid="metric-label"] {{
            font-size: {ModernTheme.FONT_SIZES['sm']};
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            font-size: {ModernTheme.FONT_SIZES['2xl']};
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-delta"] {{
            font-size: {ModernTheme.FONT_SIZES['sm']};
            font-weight: 500;
            margin-top: 0.25rem;
        }}
        
        /* Enhanced Button Styles */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
            color: {ModernTheme.TEXT_WHITE};
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            font-weight: 600;
            border-radius: var(--radius-md);
            transition: all var(--transition);
            box-shadow: var(--shadow-sm);
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
            box-shadow: var(--shadow-sm);
        }}
        
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        
        .stButton > button:hover::before {{
            left: 100%;
        }}
        
        /* Secondary Button Style */
        .secondary-button > button {{
            background: {ModernTheme.TEXT_WHITE};
            color: var(--text-primary);
            border: 1px solid var(--border);
        }}
        
        .secondary-button > button:hover {{
            background-color: var(--surface);
            border-color: var(--accent);
            color: var(--accent);
        }}
        
        /* Enhanced Form Styles */
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
        
        /* Enhanced Tab Styles */
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
            color: var(--text-secondary);
            font-weight: 500;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            transition: all var(--transition);
            border: none;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {ModernTheme.HOVER_OVERLAY};
            color: var(--text-primary);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%) !important;
            color: {ModernTheme.TEXT_WHITE} !important;
            box-shadow: var(--shadow-sm);
            font-weight: 600;
        }}
        
        /* Enhanced Status Badges */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.375rem 0.875rem;
            border-radius: 9999px;
            font-size: {ModernTheme.FONT_SIZES['xs']};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid;
        }}
        
        .status-new {{
            background-color: {ModernTheme.INFO_BG};
            color: {ModernTheme.INFO};
            border-color: {ModernTheme.INFO_BORDER};
        }}
        
        .status-active {{
            background-color: {ModernTheme.SUCCESS_BG};
            color: {ModernTheme.SUCCESS};
            border-color: {ModernTheme.SUCCESS_BORDER};
        }}
        
        .status-completed {{
            background-color: {ModernTheme.SUCCESS_BG};
            color: {ModernTheme.SUCCESS};
            border-color: {ModernTheme.SUCCESS_BORDER};
        }}
        
        .status-on-hold {{
            background-color: {ModernTheme.WARNING_BG};
            color: {ModernTheme.WARNING};
            border-color: {ModernTheme.WARNING_BORDER};
        }}
        
        .status-cancelled {{
            background-color: {ModernTheme.ERROR_BG};
            color: {ModernTheme.ERROR};
            border-color: {ModernTheme.ERROR_BORDER};
        }}
        
        /* Enhanced Info Box Styles */
        .info-box {{
            background-color: {ModernTheme.INFO_BG};
            border: 1px solid {ModernTheme.INFO_BORDER};
            color: var(--text-primary);
            padding: 1.25rem;
            border-radius: var(--radius-md);
            margin: 1rem 0;
            border-left: 4px solid {ModernTheme.INFO};
        }}
        
        .success-box {{
            background-color: {ModernTheme.SUCCESS_BG};
            border: 1px solid {ModernTheme.SUCCESS_BORDER};
            color: var(--text-primary);
            padding: 1.25rem;
            border-radius: var(--radius-md);
            margin: 1rem 0;
            border-left: 4px solid {ModernTheme.SUCCESS};
        }}
        
        .warning-box {{
            background-color: {ModernTheme.WARNING_BG};
            border: 1px solid {ModernTheme.WARNING_BORDER};
            color: var(--text-primary);
            padding: 1.25rem;
            border-radius: var(--radius-md);
            margin: 1rem 0;
            border-left: 4px solid {ModernTheme.WARNING};
        }}
        
        .error-box {{
            background-color: {ModernTheme.ERROR_BG};
            border: 1px solid {ModernTheme.ERROR_BORDER};
            color: var(--text-primary);
            padding: 1.25rem;
            border-radius: var(--radius-md);
            margin: 1rem 0;
            border-left: 4px solid {ModernTheme.ERROR};
        }}
        
        /* Enhanced Table Styles */
        .dataframe {{
            border: none !important;
            font-size: {ModernTheme.FONT_SIZES['sm']};
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
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
        
        /* Enhanced Plotly Chart Container */
        .js-plotly-plot {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            padding: 1.5rem;
            background: {ModernTheme.TEXT_WHITE};
            box-shadow: var(--shadow-sm);
            transition: all var(--transition);
        }}
        
        .js-plotly-plot:hover {{
            box-shadow: var(--shadow-md);
        }}
        
        /* Enhanced Expander */
        .streamlit-expanderHeader {{
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem;
            font-weight: 600;
            transition: all var(--transition);
        }}
        
        .streamlit-expanderHeader:hover {{
            background-color: {ModernTheme.BACKGROUND_ALT};
            border-color: var(--accent-light);
        }}
        
        /* Loading States */
        .stSpinner > div {{
            border-color: var(--accent) !important;
        }}
        
        /* Success/Error Message Styling */
        .stSuccess {{
            background-color: {ModernTheme.SUCCESS_BG};
            border: 1px solid {ModernTheme.SUCCESS_BORDER};
            border-left: 4px solid {ModernTheme.SUCCESS};
            border-radius: var(--radius-md);
            padding: 1rem;
        }}
        
        .stError {{
            background-color: {ModernTheme.ERROR_BG};
            border: 1px solid {ModernTheme.ERROR_BORDER};
            border-left: 4px solid {ModernTheme.ERROR};
            border-radius: var(--radius-md);
            padding: 1rem;
        }}
        
        .stWarning {{
            background-color: {ModernTheme.WARNING_BG};
            border: 1px solid {ModernTheme.WARNING_BORDER};
            border-left: 4px solid {ModernTheme.WARNING};
            border-radius: var(--radius-md);
            padding: 1rem;
        }}
        
        .stInfo {{
            background-color: {ModernTheme.INFO_BG};
            border: 1px solid {ModernTheme.INFO_BORDER};
            border-left: 4px solid {ModernTheme.INFO};
            border-radius: var(--radius-md);
            padding: 1rem;
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
            
            .modern-card {{
                padding: 1.25rem;
                margin-bottom: 1rem;
            }}
            
            [data-testid="metric-container"] {{
                padding: 1rem;
            }}
        }}
    </style>
    """