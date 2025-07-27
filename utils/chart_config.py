# utils/chart_config.py

from utils.theme import ModernTheme
import plotly.graph_objects as go

def get_chart_layout(title="", height=350):
    """Get consistent chart layout configuration"""
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
            'color': ModernTheme.TEXT_SECONDARY
        },
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'margin': dict(t=40, b=40, l=40, r=40),
        'height': height,
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': ModernTheme.PRIMARY,
            'font_size': 12,
            'font_family': 'Inter, sans-serif'
        },
        'xaxis': {
            'gridcolor': ModernTheme.BORDER,
            'linecolor': ModernTheme.BORDER,
            'tickfont': {
                'size': 11,
                'color': ModernTheme.TEXT_SECONDARY
            }
        },
        'yaxis': {
            'gridcolor': ModernTheme.BORDER,
            'linecolor': ModernTheme.BORDER,
            'tickfont': {
                'size': 11,
                'color': ModernTheme.TEXT_SECONDARY
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
    """Apply consistent styling to pie charts"""
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=2)
        )
    )
    return fig

def style_bar_chart(fig):
    """Apply consistent styling to bar charts"""
    fig.update_traces(
        marker=dict(
            line=dict(color='white', width=1.5)
        ),
        hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
    )
    return fig