# utils/theme.py - Enhanced Modern Theme System

class ModernTheme:
    """Enhanced modern theme configuration with better contrast and accessibility"""
    
    # Brand Colors - Professional Blue-Gray System
    PRIMARY = "#0f172a"          # Slate-900 - Deep professional navy
    PRIMARY_LIGHT = "#1e293b"    # Slate-800 - Slightly lighter
    PRIMARY_HOVER = "#334155"    # Slate-700 - Interactive states
    
    # Accent Colors - Vibrant but professional
    ACCENT = "#2563eb"           # Blue-600 - Primary actions
    ACCENT_HOVER = "#1d4ed8"     # Blue-700 - Hover state
    ACCENT_LIGHT = "#dbeafe"     # Blue-100 - Light backgrounds
    ACCENT_DARK = "#1e40af"      # Blue-800 - Dark variant
    
    # Background System
    BACKGROUND = "#ffffff"        # Pure white
    BACKGROUND_ALT = "#f8fafc"   # Slate-50 - Alternative background
    SURFACE = "#ffffff"          # Card backgrounds
    SURFACE_HOVER = "#f1f5f9"    # Slate-100 - Hover states
    
    # Border and Divider System
    BORDER = "#e2e8f0"           # Slate-200 - Subtle borders
    BORDER_STRONG = "#cbd5e1"    # Slate-300 - Stronger borders
    DIVIDER = "#f1f5f9"          # Slate-100 - Section dividers
    
    # Text Colors - High contrast for accessibility
    TEXT_PRIMARY = "#0f172a"     # Slate-900 - Main text (high contrast)
    TEXT_SECONDARY = "#475569"   # Slate-600 - Secondary text
    TEXT_MUTED = "#64748b"       # Slate-500 - Muted text
    TEXT_LIGHT = "#94a3b8"       # Slate-400 - Light text
    TEXT_WHITE = "#ffffff"       # White text for dark backgrounds
    
    # Status Colors - Vibrant and clear
    SUCCESS = "#059669"          # Emerald-600 - Success states
    SUCCESS_BG = "#d1fae5"       # Emerald-100 - Success backgrounds
    SUCCESS_BORDER = "#a7f3d0"   # Emerald-200 - Success borders
    
    WARNING = "#d97706"          # Amber-600 - Warning states
    WARNING_BG = "#fef3c7"       # Amber-100 - Warning backgrounds
    WARNING_BORDER = "#fde68a"   # Amber-200 - Warning borders
    
    ERROR = "#dc2626"            # Red-600 - Error states
    ERROR_BG = "#fee2e2"         # Red-100 - Error backgrounds
    ERROR_BORDER = "#fecaca"     # Red-200 - Error borders
    
    INFO = "#2563eb"             # Blue-600 - Info states
    INFO_BG = "#dbeafe"          # Blue-100 - Info backgrounds
    INFO_BORDER = "#bfdbfe"      # Blue-200 - Info borders
    
    # Financial Status Colors
    PROFIT = "#059669"           # Green for profits
    LOSS = "#dc2626"             # Red for losses
    NEUTRAL = "#6b7280"          # Gray for neutral
    
    # Shadows - Subtle depth
    SHADOW_XS = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    
    # Interactive States
    HOVER_OVERLAY = "rgba(0, 0, 0, 0.05)"
    ACTIVE_OVERLAY = "rgba(0, 0, 0, 0.1)"
    FOCUS_RING = "0 0 0 3px rgba(37, 99, 235, 0.1)"
    
    # Border Radius - Consistent spacing
    RADIUS_XS = "0.125rem"       # 2px
    RADIUS_SM = "0.25rem"        # 4px
    RADIUS_MD = "0.375rem"       # 6px
    RADIUS_LG = "0.5rem"         # 8px
    RADIUS_XL = "0.75rem"        # 12px
    RADIUS_2XL = "1rem"          # 16px
    RADIUS_3XL = "1.5rem"        # 24px
    
    # Spacing System
    SPACING = {
        'xs': '0.25rem',   # 4px
        'sm': '0.5rem',    # 8px
        'md': '0.75rem',   # 12px
        'lg': '1rem',      # 16px
        'xl': '1.5rem',    # 24px
        '2xl': '2rem',     # 32px
        '3xl': '3rem',     # 48px
        '4xl': '4rem'      # 64px
    }
    
    # Typography Scale
    FONT_SIZES = {
        'xs': '0.75rem',     # 12px
        'sm': '0.875rem',    # 14px
        'base': '1rem',      # 16px
        'lg': '1.125rem',    # 18px
        'xl': '1.25rem',     # 20px
        '2xl': '1.5rem',     # 24px
        '3xl': '1.875rem',   # 30px
        '4xl': '2.25rem'     # 36px
    }
    
    # Animation Timing
    TRANSITION_FAST = "0.15s ease"
    TRANSITION_NORMAL = "0.2s ease"
    TRANSITION_SLOW = "0.3s ease"
    
    @classmethod
    def get_status_colors(cls, status):
        """Get status-specific colors"""
        status_map = {
            'new': {
                'bg': cls.INFO_BG,
                'border': cls.INFO_BORDER,
                'text': cls.INFO,
                'icon': '🆕'
            },
            'active': {
                'bg': cls.SUCCESS_BG,
                'border': cls.SUCCESS_BORDER,
                'text': cls.SUCCESS,
                'icon': '🟢'
            },
            'completed': {
                'bg': cls.SUCCESS_BG,
                'border': cls.SUCCESS_BORDER,
                'text': cls.SUCCESS,
                'icon': '✅'
            },
            'invoice_submitted': {
                'bg': cls.INFO_BG,
                'border': cls.INFO_BORDER,
                'text': cls.INFO,
                'icon': '📄'
            },
            'on_hold': {
                'bg': cls.WARNING_BG,
                'border': cls.WARNING_BORDER,
                'text': cls.WARNING,
                'icon': '⏸️'
            },
            'cancelled': {
                'bg': cls.ERROR_BG,
                'border': cls.ERROR_BORDER,
                'text': cls.ERROR,
                'icon': '❌'
            }
        }
        return status_map.get(status, status_map['new'])
    
    @classmethod
    def get_financial_colors(cls, value, is_percentage=False):
        """Get colors based on financial value (positive/negative)"""
        if value > 0:
            return {
                'color': cls.SUCCESS,
                'bg': cls.SUCCESS_BG,
                'border': cls.SUCCESS_BORDER
            }
        elif value < 0:
            return {
                'color': cls.ERROR,
                'bg': cls.ERROR_BG,
                'border': cls.ERROR_BORDER
            }
        else:
            return {
                'color': cls.NEUTRAL,
                'bg': cls.BACKGROUND_ALT,
                'border': cls.BORDER
            }