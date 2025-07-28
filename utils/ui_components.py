# utils/ui_components.py - Updated version

import streamlit as st
from utils.theme import ModernTheme

def create_metric_card(label, value, delta=None, delta_color="normal", help_text=None):
    """Create a modern metric card using Streamlit's native metric"""
    # Use Streamlit's native metric component with custom styling
    if delta:
        # For inverse color, prepend a minus sign to make Streamlit show it in red
        if delta_color == "inverse" and not delta.startswith("-"):
            display_delta = f"-{delta}"
        else:
            display_delta = delta
        st.metric(label=label, value=value, delta=display_delta)
    else:
        st.metric(label=label, value=value)
    
    if help_text:
        st.caption(help_text)

def create_modern_header(title, subtitle=None):
    """Create a modern header with gradient background"""
    header_html = f"""
    <div class="modern-header">
        <h1>{title}</h1>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def create_section_header(title, icon=None):
    """Create a modern section header"""
    # Use Streamlit's native markdown for better compatibility
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")
    
    # Add a subtle divider
    st.markdown(
        f'<hr style="margin: 0.5rem 0 1.5rem 0; border: none; border-top: 2px solid {ModernTheme.BORDER};">',
        unsafe_allow_html=True
    )

def create_info_card(content, type="info"):
    """Create an info/warning/success/error card"""
    type_mapping = {
        "info": ("ℹ️", "info-box"),
        "success": ("✅", "success-box"),
        "warning": ("⚠️", "warning-box"),
        "error": ("❌", "error-box")
    }
    
    icon, css_class = type_mapping.get(type, ("ℹ️", "info-box"))
    
    card_html = f"""
    <div class="{css_class}">
        <strong>{icon}</strong> {content}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def create_status_badge(status):
    """Create a modern status badge"""
    status_map = {
        'new': ('New', 'status-new'),
        'active': ('Active', 'status-active'),
        'completed': ('Completed', 'status-completed'),
        'on_hold': ('On Hold', 'status-on-hold'),
        'cancelled': ('Cancelled', 'status-cancelled'),
        'invoice_submitted': ('Invoice Submitted', 'status-completed')
    }
    
    display_text, css_class = status_map.get(status, (status.title(), 'status-new'))
    
    badge_html = f'<span class="status-badge {css_class}">{display_text}</span>'
    
    return badge_html

def style_metric_delta(value, prefix="", suffix="", reverse=False):
    """Style metric delta with color and arrow"""
    if value == 0:
        return f"{prefix}0{suffix}"
    
    is_positive = value > 0
    if reverse:
        is_positive = not is_positive
    
    arrow = "↑" if value > 0 else "↓"
    color = ModernTheme.SUCCESS if is_positive else ModernTheme.ERROR
    
    return f'<span style="color: {color};">{arrow} {prefix}{abs(value):,.0f}{suffix}</span>'

def create_empty_state(title, description, icon="📋", action_button=None):
    """Create an empty state component"""
    # Create a centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding: 3rem;
                background-color: {ModernTheme.SURFACE};
                border-radius: {ModernTheme.RADIUS_LG};
                border: 1px solid {ModernTheme.BORDER};
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
                <h3 style="margin: 0 0 0.5rem 0; color: {ModernTheme.TEXT_PRIMARY};">{title}</h3>
                <p style="color: {ModernTheme.TEXT_SECONDARY}; margin: 0;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def create_card_container(content):
    """Create a card container for content"""
    return f"""
    <div class="modern-card">
        {content}
    </div>
    """