# utils/ui_components.py - Simplified Compatible UI Components

import streamlit as st
from utils.theme import ModernTheme
import plotly.graph_objects as go

def create_enhanced_metric_card(label, value, delta=None, delta_color="normal", help_text=None, icon=None, trend_data=None):
    """Create an enhanced metric card using Streamlit's native components with custom styling"""
    
    # Use Streamlit's native metric but enhance with custom container
    with st.container():
        # Add custom styling for the metric container
        st.markdown(f"""
        <style>
        div[data-testid="metric-container"] {{
            background: linear-gradient(135deg, {ModernTheme.SURFACE} 0%, {ModernTheme.BACKGROUND_ALT} 100%);
            border: 1px solid {ModernTheme.BORDER};
            padding: 1rem;
            border-radius: {ModernTheme.RADIUS_LG};
            box-shadow: {ModernTheme.SHADOW_SM};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Display icon and label together if icon provided
        if icon:
            st.markdown(f"### {icon} {label}")
        
        # Use Streamlit's native metric
        st.metric(
            label=label if not icon else "",
            value=value,
            delta=delta,
            help=help_text
        )

def create_modern_header(title, subtitle=None, icon=None, actions=None):
    """Create a modern header using Streamlit components"""
    
    # Create header with custom styling
    header_html = f"""
    <div style="
        background: linear-gradient(135deg, {ModernTheme.PRIMARY} 0%, {ModernTheme.PRIMARY_LIGHT} 100%);
        color: white;
        padding: 2rem;
        border-radius: {ModernTheme.RADIUS_XL};
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
            {icon + ' ' if icon else ''}{title}
        </h1>
        {f'<p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def create_section_header(title, icon=None, description=None):
    """Create a section header using Streamlit markdown"""
    
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")
    
    if description:
        st.markdown(f"*{description}*")
    
    # Add a divider
    st.markdown("---")

def create_info_card(title, content, type="info", icon=None, actions=None):
    """Create info cards using Streamlit's native alert components"""
    
    # Map types to Streamlit's native components
    if type == "info":
        st.info(f"{icon + ' ' if icon else ''}**{title}**\n\n{content}")
    elif type == "success":
        st.success(f"{icon + ' ' if icon else ''}**{title}**\n\n{content}")
    elif type == "warning":
        st.warning(f"{icon + ' ' if icon else ''}**{title}**\n\n{content}")
    elif type == "error":
        st.error(f"{icon + ' ' if icon else ''}**{title}**\n\n{content}")

def create_status_badge(status, text=None):
    """Create a status badge using simple HTML"""
    
    status_config = ModernTheme.get_status_colors(status)
    display_text = text or status.replace('_', ' ').title()
    
    badge_html = f"""
    <span style="
        background-color: {status_config['bg']};
        color: {status_config['text']};
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid {status_config['border']};
    ">
        {status_config['icon']} {display_text}
    </span>
    """
    
    return badge_html

def create_progress_bar(percentage, label=None, color=None, height="8px"):
    """Create a progress bar using Streamlit's native progress"""
    
    if label:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{label}**")
        with col2:
            st.markdown(f"**{percentage:.0f}%**")
    
    # Use Streamlit's native progress bar
    st.progress(percentage / 100)

def create_empty_state(title, description, icon="📋", actions=None):
    """Create an empty state using Streamlit components"""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 3rem 1rem;
            background-color: {ModernTheme.SURFACE};
            border-radius: {ModernTheme.RADIUS_LG};
            border: 2px dashed {ModernTheme.BORDER};
            margin: 2rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: {ModernTheme.TEXT_PRIMARY}; margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: {ModernTheme.TEXT_SECONDARY};">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add action buttons
        if actions:
            for i, (label, callback) in enumerate(actions):
                if st.button(label, key=f"empty_action_{i}"):
                    callback()

def create_stat_grid(stats_data, columns=4):
    """Create a grid of statistics using Streamlit columns"""
    
    # Create columns
    cols = st.columns(columns)
    
    for i, stat in enumerate(stats_data):
        with cols[i % columns]:
            # Use Streamlit's native metric with enhanced styling
            if stat.get('icon'):
                st.markdown(f"### {stat['icon']}")
            
            st.metric(
                label=stat.get('label', ''),
                value=stat.get('value', ''),
                delta=stat.get('delta'),
                help=stat.get('help_text')
            )

def create_data_table(data, title=None, searchable=True, paginated=True):
    """Create an enhanced data table"""
    
    if title:
        st.subheader(f"📊 {title}")
    
    # Add search functionality
    if searchable and len(data) > 0:
        search_term = st.text_input(
            "🔍 Search table",
            placeholder="Type to search...",
            key=f"search_{title}_{id(data)}"
        )
        
        if search_term:
            # Simple search across all columns
            mask = data.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            data = data[mask]
    
    # Display table
    if len(data) > 0:
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True,
            height=400 if paginated else None
        )
    else:
        create_empty_state(
            title="No Data Found",
            description="No records match your search criteria" if searchable and 'search_term' in locals() else "No data available",
            icon="📭"
        )

def create_action_button(label, callback, style="primary", icon=None, full_width=False):
    """Create an action button using Streamlit's button"""
    
    button_label = f"{icon + ' ' if icon else ''}{label}"
    
    if st.button(button_label, key=f"{label}_{style}_{id(callback)}", use_container_width=full_width):
        callback()

def create_loading_spinner(text="Loading..."):
    """Create a loading spinner using Streamlit's spinner"""
    
    return st.spinner(text)

# Backward compatibility functions
def create_metric_card(label, value, delta=None, delta_color="normal", help_text=None):
    """Backward compatibility for old metric card function"""
    return create_enhanced_metric_card(label, value, delta, delta_color, help_text)