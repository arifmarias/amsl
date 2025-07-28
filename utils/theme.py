# utils/theme.py

class ModernTheme:
    """Modern theme configuration for the application"""
    
    # Primary Colors - Deep Blue-Gray palette
    PRIMARY = "#1e293b"      # Slate-800 - Main brand color
    PRIMARY_DARK = "#0f172a" # Slate-900 - Darker variant
    PRIMARY_LIGHT = "#334155" # Slate-700 - Lighter variant
    
    # Secondary Colors - Soft accent
    ACCENT = "#3b82f6"       # Blue-500 - Action buttons
    ACCENT_HOVER = "#2563eb" # Blue-600 - Hover state
    ACCENT_LIGHT = "#dbeafe" # Blue-100 - Light backgrounds
    
    # Neutral Colors
    BACKGROUND = "#ffffff"    # Pure white background
    SURFACE = "#f8fafc"      # Slate-50 - Card backgrounds
    BORDER = "#e2e8f0"       # Slate-200 - Subtle borders
    
    # Text Colors
    TEXT_PRIMARY = "#1e293b"   # Slate-800 - Main text
    TEXT_SECONDARY = "#64748b" # Slate-500 - Secondary text
    TEXT_LIGHT = "#94a3b8"     # Slate-400 - Muted text
    
    # Status Colors
    SUCCESS = "#10b981"  # Emerald-500
    WARNING = "#f59e0b"  # Amber-500
    ERROR = "#ef4444"    # Red-500
    INFO = "#3b82f6"     # Blue-500
    
    # Shadows
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    
    # Border Radius
    RADIUS_SM = "0.375rem"  # 6px
    RADIUS_MD = "0.5rem"    # 8px
    RADIUS_LG = "0.75rem"   # 12px
    RADIUS_XL = "1rem"      # 16px
    
    # Spacing
    SPACING = {
        'xs': '0.5rem',   # 8px
        'sm': '1rem',     # 16px
        'md': '1.5rem',   # 24px
        'lg': '2rem',     # 32px
        'xl': '3rem'      # 48px
    }