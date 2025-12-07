import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import html

# Country flag emojis mapping
COUNTRY_FLAGS = {
    'AT': '🇦🇹', 'BE': '🇧🇪', 'BG': '🇧🇬', 'HR': '🇭🇷', 'CY': '🇨🇾', 'CZ': '🇨🇿',
    'DK': '🇩🇰', 'EE': '🇪🇪', 'FI': '🇫🇮', 'FR': '🇫🇷', 'DE': '🇩🇪', 'EL': '🇬🇷',
    'HU': '🇭🇺', 'IE': '🇮🇪', 'IT': '🇮🇹', 'LV': '🇱🇻', 'LT': '🇱🇹', 'LU': '🇱🇺',
    'MT': '🇲🇹', 'NL': '🇳🇱', 'PL': '🇵🇱', 'PT': '🇵🇹', 'RO': '🇷🇴', 'SK': '🇸🇰',
    'SI': '🇸🇮', 'ES': '🇪🇸', 'SE': '🇸🇪', 'UK': '🇬🇧', 'NO': '🇳🇴', 'CH': '🇨🇭',
    'IS': '🇮🇸', 'LI': '🇱🇮', 'RS': '🇷🇸', 'TR': '🇹🇷', 'AL': '🇦🇱', 'BA': '🇧🇦',
    'ME': '🇲🇪', 'MK': '🇲🇰', 'XK': '🇽🇰'
}

def get_country_flag(country_code):
    """Get flag emoji for a country code"""
    return COUNTRY_FLAGS.get(country_code, '🏳️')

# Theme / colors used across the app
COLORS = {
    'background': '#0B1120',      
    'card': '#151E32',            
    'text': '#E2E8F0',            
    'text_muted': '#94A3B8',      
    'accent': '#3B82F6',          
    'accent_hover': '#2563EB',
    'graph_line_hist': '#38BDF8', 
    'graph_line_pred': '#94A3B8'
}

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap"
]

custom_css = f"""
    body {{
        font-family: 'Montserrat', sans-serif;
        background-color: {COLORS['background']};
        margin: 0;
        overflow-x: hidden;
        font-size: 1.1rem;
    }}
    
    /* Personalización del Dropdown */
    .Select-control {{
        background-color: {COLORS['card']} !important;
        border: 1px solid #334155 !important;
        border-radius: 30px !important;
        color: {COLORS['text']} !important;
        padding: 5px 15px !important;
        min-height: 50px !important;
    }}
    .Select-menu-outer {{
        background-color: {COLORS['card']} !important;
        border: 1px solid #334155 !important;
        color: {COLORS['text']} !important;
    }}
    .Select-value-label, .Select-input > input {{
        color: {COLORS['text']} !important;
        text-align: center !important;
        width: 100% !important;
    }}
    .Select-value {{
        padding-left: 0 !important;
        padding-right: 30px !important;
        text-align: center !important;
    }}
    .Select-arrow-zone {{
        position: absolute !important;
        right: 15px !important;
    }}
    .Select-placeholder {{
        color: {COLORS['text_muted']} !important;
        text-align: center !important;
    }}
    .Select--multi .Select-value {{
        background-color: {COLORS['accent']} !important;
        border-color: {COLORS['accent_hover']} !important;
        color: white !important;
    }}
    .Select--multi .Select-value-icon {{
        border-right: 1px solid {COLORS['accent_hover']} !important;
    }}
    
    /* BOTÓN TEMÁTICO MEJORADO */
    .btn-general {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_hover']} 100%);
        color: white;
        border: none;
        padding: 0 35px;
        border-radius: 30px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        height: 52px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .btn-general:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }}
    .btn-general:active {{
        transform: translateY(1px);
    }}
    
    /* PERSONALIZACIÓN DEL SLIDER (Modo Oscuro) */
    .rc-slider-mark-text {{
        color: {COLORS['text_muted']} !important;
        font-family: 'Montserrat', sans-serif;
    }}
    .rc-slider-mark-text-active {{
        color: {COLORS['text']} !important;
        font-weight: bold;
    }}
    .rc-slider-rail {{
        background-color: #334155 !important;
    }}
    .rc-slider-track {{
        background-color: {COLORS['accent']} !important;
    }}
    .rc-slider-handle {{
        border-color: {COLORS['accent']} !important;
        background-color: {COLORS['text']} !important;
        opacity: 1 !important;
    }}
    .rc-slider-handle:hover {{
        border-color: {COLORS['accent_hover']} !important;
    }}
    
    /* ANIMACIÓN PARA EL TÍTULO */
    @keyframes pulse {{
        0%, 100% {{
            filter: drop-shadow(0 0 5px {COLORS['accent']}40);
        }}
        50% {{
            filter: drop-shadow(0 0 20px {COLORS['accent']}80);
        }}
    }}
    .rc-slider-dot {{
        border-color: #334155 !important;
        background-color: {COLORS['card']} !important;
    }}
    .rc-slider-dot-active {{
        border-color: {COLORS['accent']} !important;
    }}
    
    /* Títulos */
    h1 {{ font-size: 4rem !important; }}
    h2 {{ font-size: 2rem !important; }}
    h3 {{ font-size: 1.5rem !important; }}

    /* Animaciones */
    .header-transition {{
        transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .fade-in {{
        animation: fadeIn 0.8s ease-in forwards;
        opacity: 0;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
"""

COMMON_LAYOUT_BASE = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Montserrat', color=COLORS['text'], size=14),
    margin=dict(l=40, r=20, t=60, b=40),
)

def create_europe_heatmap(df, metric_name, year):
    if df.empty: return go.Figure()
    
    # Filtrar por año seleccionado
    df_year = df[df['year'] == year]
    
    fig = px.choropleth(
        df_year, locations="iso_alpha", color="value", hover_name="country_name",
        scope="europe", color_continuous_scale="Blues", labels={'value': metric_name}
    )
    
    title_text = f"{metric_name} ({year})"
    
    fig.update_layout(
        **COMMON_LAYOUT_BASE,
        title=dict(text=title_text, font=dict(size=22, color=COLORS['text'])),
        geo=dict(
            bgcolor='rgba(0,0,0,0)', 
            showlakes=False, 
            showframe=False, 
            showcoastlines=False, 
            projection_type='mercator', 
            lataxis_range=[32, 68],
            lonaxis_range=[-20, 45],
            projection_scale=1.4,
            landcolor='#1a1a1a',
            showcountries=True,
            countrycolor='#2D3748',
            countrywidth=0.5
        ),
        coloraxis_colorbar=dict(title=None)
    )
    return fig


def create_single_country_map(selected_country_code, etl_instance):
    data_map = []
    for code, iso3 in etl_instance.iso3_map.items():
        if code in etl_instance.countries:
            data_map.append({
                'iso_alpha': iso3,
                'country': etl_instance.countries[code],
                'color_val': 1 if code == selected_country_code else 0
            })
    df_map = pd.DataFrame(data_map)
    df_map = df_map.drop_duplicates(subset=['iso_alpha'])
    
    fig = px.choropleth(
        df_map, locations="iso_alpha", color="color_val", hover_name="country", scope="europe",
        color_continuous_scale=[[0, COLORS['card']], [1, COLORS['accent']]]
    )
    fig.update_layout(
        plot_bgcolor=COLORS['background'], 
        paper_bgcolor=COLORS['background'],
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(bgcolor=COLORS['background'], showlakes=False, showframe=False, showcoastlines=False, projection_type='mercator'),
        coloraxis_showscale=False, dragmode=False 
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig


def create_trend_graph(df, title, y_axis_title):
    if df.empty: 
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos", font=dict(size=22, color=COLORS['text'])))
        return fig
        
    if 'type' not in df.columns: df['type'] = 'Histórico'
    fig = px.line(df, x='year', y='value', color='type', markers=True, title=title,
                  color_discrete_map={'Histórico': COLORS['graph_line_hist'], 'Predicción': COLORS['graph_line_pred']})
    
    layout = COMMON_LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        xaxis=dict(showgrid=False, color=COLORS['text_muted'], title=None),
        yaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title=y_axis_title),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
        title_font=dict(size=22, color=COLORS['text'])
    )
    fig.update_traces(line=dict(width=4), marker=dict(size=8))
    return fig


def create_comparison_graph(df, title, y_axis_title):
    if df.empty: 
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos", font=dict(size=22, color=COLORS['text'])))
        return fig
    
    fig = px.line(df, x='year', y='value', color='country_name', markers=True, title=title)
    
    layout = COMMON_LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        xaxis=dict(showgrid=False, color=COLORS['text_muted'], title=None),
        yaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title=y_axis_title),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
        title_font=dict(size=22, color=COLORS['text'])
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    return fig


def create_info_card(data_dict, country_name, country_code=None):
    if not data_dict: return html.Div()
    def get_val(df, money=False):
        if df.empty: return "N/A"
        try:
            v = df.iloc[-1]['value']
            if pd.isna(v): return "N/A"
            if money: return f"€ {v/1000:.1f} B" if v>1000 else f"€ {v:.0f} M"
            return f"{v/1000000:.2f} M" if v>1000000 else f"{v:,.0f}"
        except: return "N/A"

    vals = {
        'pop': get_val(data_dict['population']),
        'gdp': get_val(data_dict['gdp'], True),
        'une': (f"{data_dict['unemployment'].iloc[-1]['value']:.1f}%" if not data_dict['unemployment'].empty else "N/A"),
        'imm': get_val(data_dict['immigration'])
    }
    
    flag = get_country_flag(country_code) if country_code else ''
    style_row = {'display': 'flex', 'justifyContent': 'space-between', 'padding': '15px 0', 'borderBottom': '1px solid #334155', 'fontSize': '1.2rem', 'color': 'white'}
    return html.Div([
        html.Div([
            html.Span(flag, style={'fontSize': '3rem', 'marginRight': '15px'}) if flag else None,
            html.H2(country_name, style={'color': COLORS['accent'], 'margin': '0', 'fontSize': '2.5rem'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
        html.P("Resumen de Indicadores (Último Año)", style={'color': 'white', 'fontSize': '1.1rem', 'marginBottom': '25px'}),
        html.Div([
            html.Div([html.Span("👥 Población"), html.Span(vals['pop'], style={'fontWeight':'bold', 'color': 'white'})], style=style_row),
            html.Div([html.Span("💰 PIB"), html.Span(vals['gdp'], style={'fontWeight':'bold', 'color': 'white'})], style=style_row),
            html.Div([html.Span("📉 Desempleo"), html.Span(vals['une'], style={'fontWeight':'bold', 'color':'#ef553b'})], style=style_row),
            html.Div([html.Span("✈️ Inmigración"), html.Span(vals['imm'], style={'fontWeight':'bold', 'color': 'white'})], style={**style_row, 'border': 'none'})
        ])
    ])


def create_ranking_chart(data, title, y_axis_title, top_n=15, ascending=True):
    """Create a horizontal bar chart for rankings with gradient colors"""
    if not data:
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos", font=dict(size=22, color=COLORS['text'])))
        return fig
    
    df = pd.DataFrame(data)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos", font=dict(size=22, color=COLORS['text'])))
        return fig
    
    # Sort and get top N
    df_sorted = df.sort_values('value', ascending=ascending).head(top_n)
    
    # Create gradient colors from dark blue to light blue
    import plotly.express as px
    colors = px.colors.sequential.Blues_r[:top_n]
    if len(colors) < len(df_sorted):
        colors = colors * (len(df_sorted) // len(colors) + 1)
    colors = colors[:len(df_sorted)]
    
    # Create horizontal bar chart with gradient
    fig = go.Figure(go.Bar(
        x=df_sorted['value'],
        y=df_sorted['country_name'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=df_sorted['value'].apply(lambda x: f"{x:,.0f}"),
        textposition='outside',
        textfont=dict(color=COLORS['text'], size=12),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>',
        customdata=df_sorted[['country_name']].values
    ))
    
    layout = COMMON_LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        title=dict(text=title, font=dict(size=24, color=COLORS['text'])),
        xaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title=y_axis_title),
        yaxis=dict(showgrid=False, color=COLORS['text'], autorange='reversed'),
        showlegend=False,
        height=700,
        clickmode='event+select'
    )
    
    return fig


def create_synthetic_future_chart(real_data, synthetic_data, event_year, country_name, metric_label):
    """
    Crea gráfico comparando escenario real vs sintético (What If).
    
    Args:
        real_data: DataFrame con ['year', 'value'] del escenario real
        synthetic_data: DataFrame con ['year', 'value'] del escenario sintético
        event_year: Año del evento analizado
        country_name: Nombre del país
        metric_label: Etiqueta de la métrica
    """
    if real_data.empty or synthetic_data.empty:
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos suficientes", font=dict(size=22, color=COLORS['text'])))
        return fig
    
    fig = go.Figure()
    
    # Línea real
    fig.add_trace(go.Scatter(
        x=real_data['year'],
        y=real_data['value'],
        mode='lines+markers',
        name='Escenario Real',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8, color=COLORS['accent']),
        hovertemplate='<b>Real</b><br>Año: %{x}<br>%{y:,.2f}<extra></extra>'
    ))
    
    # Línea sintética
    fig.add_trace(go.Scatter(
        x=synthetic_data['year'],
        y=synthetic_data['value'],
        mode='lines+markers',
        name='Escenario Sintético (What If)',
        line=dict(color='#ef553b', width=3, dash='dash'),
        marker=dict(size=8, color='#ef553b', symbol='diamond'),
        hovertemplate='<b>Sintético</b><br>Año: %{x}<br>%{y:,.2f}<extra></extra>'
    ))
    
    # Línea vertical en el evento
    fig.add_vline(
        x=event_year,
        line_dash="dot",
        line_color='#fbbf24',
        line_width=2,
        annotation_text="Evento",
        annotation_position="top",
        annotation=dict(font=dict(size=14, color='#fbbf24'))
    )
    
    # Sombreado post-evento
    years = real_data['year'].tolist()
    if years:
        fig.add_vrect(
            x0=event_year, x1=max(years),
            fillcolor='#ef553b', opacity=0.08,
            layer="below", line_width=0,
            annotation_text="Zona de Impacto", annotation_position="top left"
        )
    
    layout = COMMON_LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        title=dict(text=f"Análisis What If: {country_name}", font=dict(size=24, color=COLORS['text'], weight='bold')),
        xaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title='Año'),
        yaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title=metric_label),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'], size=13)
        ),
        hovermode='x unified',
        height=550
    )
    
    return fig


def create_impact_chart(impact_data, event_year, country_name):
    """
    Crea gráfico del impacto (diferencia real - sintético).
    
    Args:
        impact_data: DataFrame con ['year', 'impact', 'phase']
        event_year: Año del evento
        country_name: Nombre del país
    """
    if impact_data.empty:
        fig = go.Figure()
        fig.update_layout(**COMMON_LAYOUT_BASE, title=dict(text="Sin datos", font=dict(size=22, color=COLORS['text'])))
        return fig
    
    # Separar pre y post
    pre_event = impact_data[impact_data['year'] < event_year]
    post_event = impact_data[impact_data['year'] >= event_year]
    
    fig = go.Figure()
    
    # Barras pre-evento (deberían estar cerca de 0)
    if not pre_event.empty:
        colors_pre = ['#94A3B8' if val >= 0 else '#64748b' for val in pre_event['impact']]
        fig.add_trace(go.Bar(
            x=pre_event['year'],
            y=pre_event['impact'],
            name='Pre-Evento (calibración)',
            marker=dict(color=colors_pre, opacity=0.7),
            hovertemplate='<b>Pre-Evento</b><br>Año: %{x}<br>Diferencia: %{y:,.2f}<extra></extra>'
        ))
    
    # Barras post-evento (el impacto real)
    if not post_event.empty:
        colors_post = [COLORS['accent'] if val >= 0 else '#ef553b' for val in post_event['impact']]
        fig.add_trace(go.Bar(
            x=post_event['year'],
            y=post_event['impact'],
            name='Post-Evento (impacto)',
            marker=dict(color=colors_post),
            hovertemplate='<b>Post-Evento</b><br>Año: %{x}<br>Impacto: %{y:,.2f}<extra></extra>'
        ))
    
    # Línea en 0
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS['text_muted'],
        line_width=1.5
    )
    
    # Línea vertical en evento
    fig.add_vline(
        x=event_year,
        line_dash="dot",
        line_color='#fbbf24',
        line_width=2
    )
    
    layout = COMMON_LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        title=dict(text=f"Impacto del Evento en {country_name}", font=dict(size=22, color=COLORS['text'])),
        xaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title='Año'),
        yaxis=dict(showgrid=True, gridcolor='#334155', color=COLORS['text_muted'], title='Impacto (Real - Sintético)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        hovermode='x',
        barmode='relative',
        height=450
    )
    
    return fig


def create_mirror_countries_card(weights_summary):
    """
    Crea tarjeta mostrando los "países espejo" con sus pesos.
    
    Args:
        weights_summary: Lista de tuplas (nombre_país, peso)
    """
    if not weights_summary:
        return html.Div([
            html.H3("Países Espejo", 
                    style={'color': COLORS['text'], 'marginBottom': '20px', 'textAlign': 'center'}),
            html.P("No disponible", style={'color': COLORS['text_muted'], 'textAlign': 'center'})
        ])
    
    # Crear barras para cada país
    weight_items = []
    for country_name, weight in weights_summary[:10]:  # Top 10
        percentage = weight * 100
        weight_items.append(
            html.Div([
                html.Div([
                    html.Span(country_name, style={'color': COLORS['text'], 'fontSize': '0.95rem'}),
                    html.Span(f"{percentage:.1f}%", 
                             style={'color': COLORS['accent'], 'fontWeight': 'bold', 'fontSize': '1rem'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '6px'}),
                html.Div([
                    html.Div(style={
                        'width': f'{percentage}%',
                        'height': '6px',
                        'backgroundColor': COLORS['accent'],
                        'borderRadius': '3px',
                        'transition': 'width 0.5s ease',
                        'boxShadow': f'0 0 8px {COLORS["accent"]}80'
                    })
                ], style={'backgroundColor': '#334155', 'borderRadius': '3px', 'height': '6px', 'marginBottom': '12px'})
            ])
        )
    
    return html.Div([
        html.H3("🔍 Países Espejo", 
                style={'color': COLORS['text'], 'marginBottom': '15px', 'fontSize': '1.4rem', 'textAlign': 'center'}),
        html.P("El escenario sintético se construye combinando:", 
               style={'color': COLORS['text_muted'], 'marginBottom': '20px', 'textAlign': 'center', 'fontSize': '0.9rem'}),
        html.Div(weight_items, style={'maxHeight': '420px', 'overflowY': 'auto', 'paddingRight': '10px'})
    ])
