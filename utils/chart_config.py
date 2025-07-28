# utils/chart_config.py - Fixed Chart Backgrounds

from utils.theme import ModernTheme
import plotly.graph_objects as go

def get_chart_layout(title="", height=350):
    """Get consistent chart layout configuration with white background"""
    return {
        'title': {
            'text': title,
            'font': {
                'size': 16,
                'color': ModernTheme.TEXT_PRIMARY,
                'family': 'Inter, sans-serif'
            }
        },
        'font': {
            'family': 'Inter, sans-serif',
            'color': ModernTheme.TEXT_PRIMARY  # Dark text
        },
        'plot_bgcolor': 'white',  # Chart area background
        'paper_bgcolor': 'white',  # Overall background
        'margin': dict(t=40, b=40, l=40, r=40),
        'height': height,
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': ModernTheme.PRIMARY,
            'font_size': 12,
            'font_family': 'Inter, sans-serif',
            'font_color': 'white'
        },
        'xaxis': {
            'gridcolor': ModernTheme.BORDER,
            'linecolor': ModernTheme.BORDER,
            'tickfont': {
                'size': 11,
                'color': ModernTheme.TEXT_PRIMARY  # Dark text
            },
            'titlefont': {
                'color': ModernTheme.TEXT_PRIMARY
            }
        },
        'yaxis': {
            'gridcolor': ModernTheme.BORDER,
            'linecolor': ModernTheme.BORDER,
            'tickfont': {
                'size': 11,
                'color': ModernTheme.TEXT_PRIMARY  # Dark text
            },
            'titlefont': {
                'color': ModernTheme.TEXT_PRIMARY
            }
        }
    }

def get_color_palette():
    """Get consistent color palette for charts"""
    return [
        ModernTheme.ACCENT,        # Blue
        ModernTheme.SUCCESS,       # Green
        ModernTheme.WARNING,       # Amber
        ModernTheme.ERROR,         # Red
        ModernTheme.PRIMARY,       # Slate
        '#8b5cf6',                 # Violet
        '#06b6d4',                 # Cyan
        '#f59e0b',                 # Orange
    ]

def style_pie_chart(fig):
    """Apply consistent styling to pie charts with white background"""
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=2)
        ),
        textfont=dict(color='white', size=12)  # White text on colored slices
    )
    
    # Ensure white background
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=ModernTheme.TEXT_PRIMARY)
    )
    
    return fig

def style_bar_chart(fig):
    """Apply consistent styling to bar charts with white background"""
    fig.update_traces(
        marker=dict(
            line=dict(color='white', width=1.5)
        ),
        hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
    )
    
    # Ensure white background
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=ModernTheme.TEXT_PRIMARY),
        xaxis=dict(
            gridcolor=ModernTheme.BORDER,
            tickfont=dict(color=ModernTheme.TEXT_PRIMARY)
        ),
        yaxis=dict(
            gridcolor=ModernTheme.BORDER,
            tickfont=dict(color=ModernTheme.TEXT_PRIMARY)
        )
    )
    
    return fig