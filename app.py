import dash
from dash import html, dcc, Input, Output, State, callback_context
import pandas as pd
import plotly.graph_objs as go

from src.etl import EurostatETL
from src.model import StatsModel
from src.graphics import (
    COLORS, external_stylesheets, custom_css,
    create_europe_heatmap, create_single_country_map,
    create_trend_graph, create_comparison_graph, create_info_card,
    get_country_flag
)

etl = EurostatETL()
model = StatsModel()

app = dash.Dash(__name__, title="EuroInfo Enhanced", external_stylesheets=external_stylesheets)
server = app.server

# Inject custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + custom_css + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    # Stores
    dcc.Store(id='view-state', data='home'), 
    dcc.Store(id='general-data-store', data={}),
    dcc.Store(id='rankings-data-store', data={}),

    # --- HEADER ---
    html.Div(id='header-container', className='header-transition', children=[
        html.Div([
            html.H1([
                html.Span("Euro", style={'color': 'white'}),
                html.Span("Info", style={'color': COLORS['accent'], 'textShadow': f'0 0 30px {COLORS["accent"]}, 0 0 60px {COLORS["accent"]}'})
            ], style={
                'fontWeight': '700', 
                'margin': '0 0 10px 0', 
                'fontSize': '4rem',
                'letterSpacing': '2px',
                'background': f'linear-gradient(135deg, white 0%, {COLORS["accent"]} 100%)',
                'WebkitBackgroundClip': 'text',
                'WebkitTextFillColor': 'transparent',
                'backgroundClip': 'text',
                'animation': 'pulse 3s ease-in-out infinite'
            }),
            html.P([
                html.Span("🌍 ", style={'fontSize': '1.5rem'}),
                "Explora, compara y predice indicadores en Europa"
            ], style={'color': COLORS['text_muted'], 'fontSize': '1.3rem', 'marginBottom': '30px'}),
            
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='country-selector',
                        options=etl.get_country_list(),
                        value=None,
                        multi=True,
                        placeholder="Selecciona uno o varios países...",
                        clearable=True
                    )
                ], style={'flex': '1'}),
                
                html.Div(style={'width': '15px'}),
                html.Button("Mapa", id='btn-general', className='btn-general'),
                html.Div(style={'width': '15px'}),
                html.Button("Rankings", id='btn-rankings', className='btn-general'),
                html.Div(style={'width': '15px'}),
                html.Button("What If", id='btn-whatif', className='btn-general')
                
            ], style={'display': 'flex', 'width': '100%', 'maxWidth': '1200px', 'alignItems': 'center'})
            
        ], style={'textAlign': 'center', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'height': '100%'})
    ]),
    
    # --- SEPARATOR ---
    html.Div(style={
        'height': '3px',
        'background': f'linear-gradient(90deg, transparent 0%, {COLORS["accent"]} 50%, transparent 100%)',
        'margin': '30px 0',
        'borderRadius': '2px',
        'boxShadow': f'0 0 20px {COLORS["accent"]}50'
    }),

    # --- VISTA 1: PERFIL DE UN PAÍS ---
    html.Div(id='country-view-container', style={'display': 'none'}, children=[
        html.Div([
            html.Div([
                dcc.Graph(id='country-map', config={'displayModeBar': False}, style={'height': '100%'})
            ], className='fade-in', style={'width': '48%', 'padding': '10px', 'height': '450px'}),
            html.Div(id='info-card-container', className='fade-in', 
                     style={'width': '48%', 'padding': '30px', 'maxHeight': '450px', 'overflowY': 'auto'})
        ], style={'display': 'flex', 'flexWrap': 'nowrap', 'marginBottom': '25px', 'justifyContent': 'space-between', 'alignItems': 'flex-start'}),

        html.Div(className='fade-in', children=[
            html.Div([
                html.Div([dcc.Loading(dcc.Graph(id='population-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'}),
                html.Div([dcc.Loading(dcc.Graph(id='immigration-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'})
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '40px'}),
            
            html.Div([
                html.Div([dcc.Loading(dcc.Graph(id='unemployment-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%'}),
                html.Div([dcc.Loading(dcc.Graph(id='gdp-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%'})
            ], style={'display': 'flex', 'gap': '20px'})
        ])
    ]),

    # --- VISTA 2: COMPARACIÓN DE PAÍSES ---
    html.Div(id='comparison-view-container', style={'display': 'none'}, children=[
        html.H2("Comparativa de Países", style={'color': COLORS['text'], 'marginBottom': '25px', 'textAlign': 'center'}),
        html.Div(className='fade-in', children=[
            html.Div([
                html.Div([dcc.Loading(dcc.Graph(id='comp-pop-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'}),
                html.Div([dcc.Loading(dcc.Graph(id='comp-gdp-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'})
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '40px'}),
            
            html.Div([
                html.Div([dcc.Loading(dcc.Graph(id='comp-une-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'}),
                html.Div([dcc.Loading(dcc.Graph(id='comp-imm-graph', style={'height': '500px'}), type="cube", color=COLORS['accent'])], 
                         style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '15px', 'width': '49%', 'marginBottom': '20px'})
            ], style={'display': 'flex', 'gap': '20px'})
        ])
    ]),

    # --- VISTA 3: VISTA GENERAL (CON SLIDER) ---
    html.Div(id='general-view-container', style={'display': 'none'}, children=[
        html.Div([
            html.H2("Mapa General de Europa", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            
            # Selector de Métrica
            dcc.Dropdown(
                id='general-metric-selector',
                options=[
                    {'label': 'Población Total', 'value': 'population'},
                    {'label': 'Tasa de Desempleo (%)', 'value': 'unemployment'},
                    {'label': 'Producto Interior Bruto (PIB)', 'value': 'gdp'},
                    {'label': 'Inmigración Anual', 'value': 'immigration'}
                ],
                value='population',
                clearable=False,
                style={'width': '400px', 'marginBottom': '20px'}
            ),

            # SLIDER DE AÑO
            html.Div([
                html.Label("Seleccionar Año:", style={'color': COLORS['text_muted'], 'marginBottom': '10px', 'display': 'block'}),
                dcc.Slider(
                    id='year-slider',
                    min=2010,
                    max=2023,
                    step=1,
                    value=2022,
                    marks={i: str(i) for i in range(2010, 2024, 2)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': '30px', 'padding': '0 20px'}),
            
            html.Div([
                dcc.Loading(dcc.Graph(id='general-map', config={'displayModeBar': False}, style={'height': '700px'}), type="cube", color=COLORS['accent'])
            ], style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '10px'})
            
        ], className='fade-in', style={'maxWidth': '1400px', 'margin': '0 auto'})
    ]),

    # --- VISTA 4: RANKINGS ---
    html.Div(id='rankings-view-container', style={'display': 'none'}, children=[
        html.Div([
            html.H2("Rankings Europeos", style={'color': COLORS['text'], 'marginBottom': '20px', 'textAlign': 'center'}),
            
            # Selector de Año
            html.Div([
                html.Label("Seleccionar Año:", style={'color': COLORS['text_muted'], 'marginBottom': '10px', 'display': 'block'}),
                dcc.Slider(
                    id='rankings-year-slider',
                    min=2010,
                    max=2023,
                    step=1,
                    value=2022,
                    marks={i: str(i) for i in range(2010, 2024, 2)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': '30px', 'padding': '0 20px'}),
            
            # Metric Selector
            dcc.Dropdown(
                id='ranking-metric-selector',
                options=[
                    {'label': 'Población Total', 'value': 'population'},
                    {'label': 'PIB', 'value': 'gdp'},
                    {'label': 'Tasa de Desempleo', 'value': 'unemployment'},
                    {'label': 'Inmigración Anual', 'value': 'immigration'}
                ],
                value='population',
                clearable=False,
                style={'width': '400px', 'marginBottom': '30px', 'margin': '0 auto'}
            ),
            
            # Rankings Chart and Info Card
            html.Div(className='fade-in', children=[
                html.Div([
                    dcc.Loading(dcc.Graph(id='ranking-chart', config={'displayModeBar': False}, style={'height': '700px'}), type="cube", color=COLORS['accent'])
                ], style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '20px', 'width': '65%'}),
                
                html.Div(id='ranking-info-card', children=[
                    html.Div([
                        html.H3("Selecciona un país", style={'color': COLORS['text'], 'textAlign': 'center', 'marginTop': '50px'}),
                        html.P("Haz clic en una barra del ranking para ver su información", 
                               style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '0.9rem'})
                    ])
                ], style={'width': '32%', 'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '30px', 'minHeight': '700px'})
            ], style={'display': 'flex', 'gap': '20px', 'justifyContent': 'center'})
            
        ], className='fade-in', style={'maxWidth': '1400px', 'margin': '0 auto'})
    ]),

    # --- VISTA 5: WHAT IF (FUTUROS SINTÉTICOS) ---
    html.Div(id='whatif-view-container', style={'display': 'none'}, children=[
        html.Div([
            html.H2("What If: Futuros Sintéticos", 
                    style={'color': COLORS['text'], 'marginBottom': '10px', 'textAlign': 'center'}),
            html.P("Explora escenarios: ¿Qué habría pasado si un evento NO hubiera ocurrido?", 
                   style={'color': COLORS['text_muted'], 'marginBottom': '35px', 'textAlign': 'center', 'fontSize': '1.05rem'}),
            
            # Panel de configuración
            html.Div([
                html.Div([
                    html.Label("País a Analizar:", 
                              style={'color': COLORS['text'], 'marginBottom': '8px', 'display': 'block', 'fontWeight': '600'}),
                    dcc.Dropdown(
                        id='whatif-country-selector',
                        options=etl.get_country_list(),
                        value='UK',
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
                
                html.Div([
                    html.Label("Año del Evento:", 
                              style={'color': COLORS['text'], 'marginBottom': '8px', 'display': 'block', 'fontWeight': '600'}),
                    dcc.Dropdown(
                        id='whatif-year-selector',
                        options=[{'label': str(y), 'value': y} for y in range(2010, 2020)],
                        value=2016,
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '150px'})
                
            ], style={'display': 'flex', 'gap': '25px', 'marginBottom': '30px', 'justifyContent': 'center', 'maxWidth': '800px', 'margin': '0 auto 30px'}),
            
            # Botón de análisis
            html.Div([
                html.Button("🔮 Ejecutar Análisis", 
                           id='btn-run-whatif', 
                           className='btn-general',
                           style={'fontSize': '1.15rem', 'padding': '0 45px', 'height': '55px'})
            ], style={'textAlign': 'center', 'marginBottom': '40px'}),
            
            # Contenedor de resultados
            html.Div(id='whatif-results-container', children=[
                html.Div([
                    html.Div("🎯", style={'fontSize': '4rem', 'marginBottom': '20px'}),
                    html.P("Selecciona un país y año del evento, luego haz clic en 'Ejecutar Análisis'", 
                           style={'color': COLORS['text_muted'], 'fontSize': '1.1rem', 'lineHeight': '1.6'})
                ], style={'textAlign': 'center', 'marginTop': '80px'})
            ])
            
        ], className='fade-in', style={'maxWidth': '1400px', 'margin': '0 auto'})
    ])

], style={'minHeight': '100vh', 'padding': '0 20px'})

# ==========================================
# CALLBACKS
# ==========================================
@app.callback(
    [Output('view-state', 'data'),
     Output('country-selector', 'value')],
    [Input('country-selector', 'value'),
     Input('btn-general', 'n_clicks'),
     Input('btn-rankings', 'n_clicks'),
     Input('btn-whatif', 'n_clicks')],
    [State('view-state', 'data')]
)
def manage_view_state(country_val, btn_general_clicks, btn_rankings_clicks, btn_whatif_clicks, current_state):
    ctx = callback_context
    if not ctx.triggered:
        return 'home', dash.no_update
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'country-selector':
        if not country_val: return 'home', None
        if isinstance(country_val, list):
            if len(country_val) > 1: return 'comparison', country_val
            if len(country_val) == 1: return 'country', country_val 
            return 'home', None
        else: return 'country', country_val

    if trigger_id == 'btn-general': return 'general', None
    if trigger_id == 'btn-rankings': return 'rankings', None
    if trigger_id == 'btn-whatif': return 'whatif', None
    return current_state, dash.no_update

@app.callback(
    [Output('header-container', 'style'),
     Output('country-view-container', 'style'),
     Output('comparison-view-container', 'style'),
     Output('general-view-container', 'style'),
     Output('rankings-view-container', 'style'),
     Output('whatif-view-container', 'style')],
    [Input('view-state', 'data')]
)
def update_layout_visibility(view_state):
    header_full = {'height': '100vh', 'paddingTop': '0'}
    header_collapsed = {'height': '20vh', 'paddingTop': '20px'}
    hidden = {'display': 'none'}
    visible = {'display': 'block', 'maxWidth': '1400px', 'margin': '0 auto', 'paddingBottom': '50px'}

    if view_state == 'home': return header_full, hidden, hidden, hidden, hidden, hidden
    elif view_state == 'country': return header_collapsed, visible, hidden, hidden, hidden, hidden
    elif view_state == 'comparison': return header_collapsed, hidden, visible, hidden, hidden, hidden
    elif view_state == 'general': return header_collapsed, hidden, hidden, visible, hidden, hidden
    elif view_state == 'rankings': return header_collapsed, hidden, hidden, hidden, visible, hidden
    elif view_state == 'whatif': return header_collapsed, hidden, hidden, hidden, hidden, visible
    return header_full, hidden, hidden, hidden, hidden, hidden

# --- Perfil Individual ---
@app.callback(
    [Output('info-card-container', 'children'),
     Output('country-map', 'figure'),
     Output('population-graph', 'figure'),
     Output('immigration-graph', 'figure'),
     Output('unemployment-graph', 'figure'),
     Output('gdp-graph', 'figure')],
    [Input('view-state', 'data'),
     Input('country-selector', 'value')]
)
def update_country_view(view_state, country_selection):
    if view_state != 'country' or not country_selection:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    code = country_selection[0] if isinstance(country_selection, list) else country_selection

    data = etl.get_country_profile(code)
    country_name = etl.get_country_name(code)
    info_card = create_info_card(data, country_name, code)
    map_fig = create_single_country_map(code, etl)
    
    df_pop = model.predict_next_years(data['population'])
    fig_pop = create_trend_graph(df_pop, "Población", "Habitantes")
    df_imm = model.predict_next_years(data['immigration'])
    fig_imm = create_trend_graph(df_imm, "Inmigración", "Personas")
    df_une = model.predict_next_years(data['unemployment'])
    fig_une = create_trend_graph(df_une, "Desempleo", "%")
    df_gdp = model.predict_next_years(data['gdp'])
    fig_gdp = create_trend_graph(df_gdp, "PIB", "Millones €")

    return info_card, map_fig, fig_pop, fig_imm, fig_une, fig_gdp

# --- Comparación ---
@app.callback(
    [Output('comp-pop-graph', 'figure'),
     Output('comp-gdp-graph', 'figure'),
     Output('comp-une-graph', 'figure'),
     Output('comp-imm-graph', 'figure')],
    [Input('view-state', 'data'),
     Input('country-selector', 'value')]
)
def update_comparison_view(view_state, country_codes):
    if view_state != 'comparison' or not country_codes:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    data_all = etl.get_comparison_data(country_codes)
    fig_pop = create_comparison_graph(data_all['population'], "Comparativa Población", "Habitantes")
    fig_gdp = create_comparison_graph(data_all['gdp'], "Comparativa PIB", "Millones €")
    fig_une = create_comparison_graph(data_all['unemployment'], "Comparativa Desempleo", "% Tasa")
    fig_imm = create_comparison_graph(data_all['immigration'], "Comparativa Inmigración", "Personas")
    return fig_pop, fig_gdp, fig_une, fig_imm

# --- Mapa General: 1. Cargar Datos al Store ---
@app.callback(
    Output('general-data-store', 'data'),
    [Input('view-state', 'data'),
     Input('general-metric-selector', 'value')]
)
def fetch_general_data(view_state, metric):
    if view_state != 'general': return dash.no_update
    
    filters = {}
    if metric == 'population': filters = {'sex': 'T', 'age': 'TOTAL'}
    elif metric == 'unemployment': filters = {'age': 'Y15-74', 'sex': 'T'}
    elif metric == 'immigration': filters = {'age': 'TOTAL', 'sex': 'T'}
    elif metric == 'gdp': filters = {'unit': 'CP_MEUR', 'na_item': 'B1GQ'}

    df = etl.get_full_data_for_metric(metric, filters)
    return df.to_dict('records')

# --- Mapa General: 2. Actualizar Slider ---
@app.callback(
    [Output('year-slider', 'min'),
     Output('year-slider', 'max'),
     Output('year-slider', 'marks'),
     Output('year-slider', 'value')],
    [Input('general-data-store', 'data')]
)
def update_slider_config(data):
    if not data: return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    df = pd.DataFrame(data)
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    
    # Marcas cada 2 o 5 años dependiendo del rango
    step = 2 if (max_year - min_year) < 20 else 5
    marks = {i: str(i) for i in range(min_year, max_year + 1, step)}
    marks[max_year] = str(max_year) # Asegurar que el último año tenga marca
    
    return min_year, max_year, marks, max_year

# --- Mapa General: 3. Actualizar Mapa ---
@app.callback(
    Output('general-map', 'figure'),
    [Input('year-slider', 'value'),
     Input('general-metric-selector', 'value'),
     Input('general-data-store', 'data')]
)
def update_map_figure(year, metric, data):
    if not data or not year: return dash.no_update
    
    df = pd.DataFrame(data)
    
    titles = {
        'population': 'Población Total',
        'unemployment': 'Tasa de Desempleo %',
        'gdp': 'PIB Millones €',
        'immigration': 'Inmigración Total'
    }
    
    return create_europe_heatmap(df, titles.get(metric, ''), year)

# --- Rankings: Fetch all metrics data ---
@app.callback(
    Output('rankings-data-store', 'data'),
    [Input('view-state', 'data'),
     Input('rankings-year-slider', 'value')]
)
def fetch_rankings_data(view_state, year):
    if view_state != 'rankings' or not year: return dash.no_update
    
    filters_map = {
        'population': {'sex': 'T', 'age': 'TOTAL'},
        'unemployment': {'age': 'Y15-74', 'sex': 'T'},
        'gdp': {'unit': 'CP_MEUR', 'na_item': 'B1GQ'},
        'immigration': {'age': 'TOTAL', 'sex': 'T'}
    }
    
    all_data = {}
    for metric, filters in filters_map.items():
        df = etl.get_full_data_for_metric(metric, filters)
        if not df.empty:
            df_year = df[df['year'] == year]
            if df_year.empty:
                df_year = df.sort_values('year').groupby(df.columns[0]).tail(1)
            all_data[metric] = df_year.to_dict('records')
        else:
            all_data[metric] = []
    
    return all_data

# --- Rankings: Create ranking chart ---
@app.callback(
    Output('ranking-chart', 'figure'),
    [Input('rankings-data-store', 'data'),
     Input('ranking-metric-selector', 'value')]
)
def update_ranking_chart(data, metric):
    if not data or not metric:
        return go.Figure()
    
    from src.graphics import create_ranking_chart
    
    metric_config = {
        'population': {'title': 'Top 15 Población', 'unit': 'Habitantes'},
        'gdp': {'title': 'Top 15 PIB', 'unit': 'Millones €'},
        'unemployment': {'title': 'Top 15 Desempleo', 'unit': '% Tasa'},
        'immigration': {'title': 'Top 15 Inmigración', 'unit': 'Personas'}
    }
    
    config = metric_config.get(metric, {'title': 'Ranking', 'unit': ''})
    return create_ranking_chart(data.get(metric, []), config['title'], config['unit'], top_n=15, ascending=False)

# --- Rankings: Update info card on click ---
@app.callback(
    Output('ranking-info-card', 'children'),
    [Input('ranking-chart', 'clickData'),
     Input('rankings-data-store', 'data'),
     Input('ranking-metric-selector', 'value')]
)
def update_ranking_info_card(clickData, data, metric):
    from src.graphics import get_country_flag
    
    if not clickData or not data or not metric:
        return html.Div([
            html.H3("Selecciona un país", style={'color': COLORS['text'], 'textAlign': 'center', 'marginTop': '50px'}),
            html.P("Haz clic en una barra del ranking para ver su información", 
                   style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '0.9rem'})
        ])
    
    country_name = clickData['points'][0]['y']
    df = pd.DataFrame(data.get(metric, []))
    
    if df.empty:
        return html.Div([html.P("No hay datos disponibles", style={'color': COLORS['text_muted']})])
    
    # Sort to get rankings
    df_sorted = df.sort_values('value', ascending=False).reset_index(drop=True)
    country_row = df_sorted[df_sorted['country_name'] == country_name]
    
    if country_row.empty:
        return html.Div([html.P("País no encontrado", style={'color': COLORS['text_muted']})])
    
    position = country_row.index[0] + 1
    value = country_row.iloc[0]['value']
    country_code = country_row.iloc[0].get('geo', '')
    flag = get_country_flag(country_code) if country_code else ''
    
    total_countries = len(df_sorted)
    
    metric_labels = {
        'population': 'Población',
        'gdp': 'PIB',
        'unemployment': 'Desempleo',
        'immigration': 'Inmigración'
    }
    
    metric_units = {
        'population': f"{value/1000000:.2f}M habitantes" if value > 1000000 else f"{value:,.0f} habitantes",
        'gdp': f"€{value/1000:.1f}B" if value > 1000 else f"€{value:.0f}M",
        'unemployment': f"{value:.1f}%",
        'immigration': f"{value/1000:.1f}K personas" if value > 1000 else f"{value:,.0f} personas"
    }
    
    return html.Div([
        html.Div([
            html.Span(flag, style={'fontSize': '4rem', 'marginBottom': '10px', 'display': 'block', 'textAlign': 'center'}) if flag else None,
            html.H2(country_name, style={'color': COLORS['accent'], 'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '2rem'})
        ]),
        
        html.Div([
            html.Div([
                html.Div(str(position), style={
                    'fontSize': '5rem',
                    'fontWeight': 'bold',
                    'color': COLORS['accent'],
                    'textAlign': 'center',
                    'lineHeight': '1'
                }),
                html.P(f"de {total_countries}", style={
                    'color': COLORS['text_muted'],
                    'textAlign': 'center',
                    'fontSize': '1.2rem',
                    'marginTop': '5px'
                })
            ], style={'marginBottom': '30px'}),
            
            html.Div([
                html.P("Posición en el ranking", style={'color': COLORS['text_muted'], 'fontSize': '0.9rem', 'marginBottom': '20px', 'textAlign': 'center'}),
                
                html.Div([
                    html.Span(f"📊 {metric_labels.get(metric, '')}", style={'color': COLORS['text'], 'fontSize': '1.1rem'}),
                    html.Span(metric_units.get(metric, str(value)), style={'fontWeight': 'bold', 'color': 'white', 'fontSize': '1.3rem', 'display': 'block', 'marginTop': '10px'})
                ], style={
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'borderRadius': '10px',
                    'padding': '20px',
                    'borderLeft': f'4px solid {COLORS["accent"]}',
                    'marginTop': '20px'
                })
            ])
        ])
    ], style={'color': 'white'})

# --- What If: Synthetic Future Analysis ---
@app.callback(
    Output('whatif-results-container', 'children'),
    [Input('btn-run-whatif', 'n_clicks')],
    [State('whatif-country-selector', 'value'),
     State('whatif-year-selector', 'value')]
)
def run_whatif_analysis(n_clicks, country_code, event_year):
    from src.model import SyntheticFutureModel
    from src.graphics import create_synthetic_future_chart, create_impact_chart, create_mirror_countries_card
    
    if not n_clicks:
        return html.Div([
            html.Div("🎯", style={'fontSize': '4rem', 'marginBottom': '20px'}),
            html.P("Selecciona un país y año del evento, luego haz clic en 'Ejecutar Análisis'", 
                   style={'color': COLORS['text_muted'], 'fontSize': '1.1rem', 'lineHeight': '1.6'})
        ], style={'textAlign': 'center', 'marginTop': '80px'})
    
    if not country_code or not event_year:
        return html.Div([
            html.P("⚠️ Por favor, selecciona país y año del evento", 
                   style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
        ])
    
    try:
        # 1. Obtener datos brutos
        raw_data = etl.get_data_for_synthetic_future()
        
        if not all(key in raw_data for key in ['population', 'gdp', 'unemployment', 'immigration']):
            return html.Div([
                html.P("❌ Error: No se pudieron obtener los datos necesarios", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
            ])
        
        # 2. Transformar datos (PIB per cápita, tasas comparables)
        model = SyntheticFutureModel()
        transformed_data = model.transform_data(raw_data)
        
        if 'gdp_per_capita' not in transformed_data or transformed_data['gdp_per_capita'].empty:
            return html.Div([
                html.P("❌ Error al transformar los datos", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
            ])
        
        # 3. Preparar datos del país objetivo
        geo_col = [col for col in transformed_data['gdp_per_capita'].columns if 'geo' in col.lower()][0]
        
        target_df = transformed_data['gdp_per_capita'][
            transformed_data['gdp_per_capita'][geo_col] == country_code
        ][['year', 'value']].copy()
        
        if target_df.empty:
            return html.Div([
                html.P(f"❌ No hay datos disponibles para {etl.get_country_name(country_code)}", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
            ])
        
        # 4. Preparar países donantes (todos menos el objetivo)
        donor_dict = {}
        for donor_code in etl.countries.keys():
            if donor_code != country_code:
                donor_df = transformed_data['gdp_per_capita'][
                    transformed_data['gdp_per_capita'][geo_col] == donor_code
                ][['year', 'value']].copy()
                
                if not donor_df.empty:
                    donor_dict[donor_code] = donor_df
        
        if len(donor_dict) < 5:
            return html.Div([
                html.P("❌ No hay suficientes países donantes para el análisis", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
            ])
        
        # 5. Entrenar modelo (estrategia del espejo)
        weights = model.fit(target_df, donor_dict, event_year, metric='gdp_per_capita')
        
        if weights is None:
            return html.Div([
                html.P("❌ No se pudo construir un escenario sintético válido. Intenta con otro país o año.", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'}),
                html.P("Consejo: El año del evento debe tener al menos 5 años de datos históricos previos.", 
                       style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '0.95rem', 'marginTop': '15px'})
            ])
        
        # 6. Generar escenario sintético (What If)
        all_years = sorted(target_df['year'].unique())
        synthetic_df = model.predict(donor_dict, all_years)
        
        if synthetic_df is None or synthetic_df.empty:
            return html.Div([
                html.P("❌ Error al generar el escenario sintético", 
                       style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1.1rem', 'marginTop': '50px'})
            ])
        
        # 7. Calcular impacto
        impact_df = model.calculate_impact(target_df, synthetic_df)
        
        # 8. Obtener países espejo
        weights_summary = model.get_weights_summary(etl)
        
        country_name = etl.get_country_name(country_code)
        
        # 9. Crear visualizaciones
        future_chart = create_synthetic_future_chart(
            target_df, synthetic_df, event_year, country_name, 'PIB per Cápita (€)'
        )
        
        impact_chart = create_impact_chart(
            impact_df, event_year, country_name
        )
        
        mirror_card = create_mirror_countries_card(weights_summary)
        
        # 10. Calcular estadísticas de impacto
        post_impact = impact_df[impact_df['year'] >= event_year]['impact']
        if not post_impact.empty:
            avg_impact = post_impact.mean()
            total_impact = post_impact.sum()
            impact_sign = "positivo" if avg_impact >= 0 else "negativo"
            impact_color = COLORS['accent'] if avg_impact >= 0 else '#ef553b'
        else:
            avg_impact = 0
            total_impact = 0
            impact_sign = "neutral"
            impact_color = COLORS['text_muted']
        
        # 11. Retornar resultados completos
        return html.Div([
            # Título de resultados
            html.Div([
                html.H3("📊 Resultados del Análisis What If", 
                        style={'color': COLORS['text'], 'marginBottom': '10px', 'textAlign': 'center'}),
                html.P([
                    "Comparando ",
                    html.Strong(country_name, style={'color': COLORS['accent']}),
                    " con su ",
                    html.Strong("escenario sintético", style={'color': '#ef553b'}),
                    f" desde {event_year}"
                ], style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '1rem', 'marginBottom': '25px'})
            ]),
            
            # Métricas de impacto
            html.Div([
                html.Div([
                    html.Span("Impacto Promedio Anual", style={'color': COLORS['text_muted'], 'fontSize': '0.9rem'}),
                    html.Span(f"{avg_impact:,.0f} €", 
                             style={'color': impact_color, 'fontWeight': 'bold', 'fontSize': '1.8rem', 'display': 'block', 'marginTop': '8px'})
                ], style={
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '12px',
                    'padding': '20px',
                    'textAlign': 'center',
                    'flex': '1',
                    'borderLeft': f'4px solid {impact_color}'
                }),
                
                html.Div([
                    html.Span("Impacto Acumulado", style={'color': COLORS['text_muted'], 'fontSize': '0.9rem'}),
                    html.Span(f"{total_impact:,.0f} €", 
                             style={'color': impact_color, 'fontWeight': 'bold', 'fontSize': '1.8rem', 'display': 'block', 'marginTop': '8px'})
                ], style={
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '12px',
                    'padding': '20px',
                    'textAlign': 'center',
                    'flex': '1',
                    'borderLeft': f'4px solid {impact_color}'
                }),
                
                html.Div([
                    html.Span("Dirección del Impacto", style={'color': COLORS['text_muted'], 'fontSize': '0.9rem'}),
                    html.Span(f"{'↗️' if avg_impact >= 0 else '↘️'} {impact_sign.capitalize()}", 
                             style={'color': impact_color, 'fontWeight': 'bold', 'fontSize': '1.8rem', 'display': 'block', 'marginTop': '8px'})
                ], style={
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '12px',
                    'padding': '20px',
                    'textAlign': 'center',
                    'flex': '1',
                    'borderLeft': f'4px solid {impact_color}'
                })
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '35px'}),
            
            # Gráfico principal + Países espejo
            html.Div([
                html.Div([
                    dcc.Loading(
                        dcc.Graph(figure=future_chart, config={'displayModeBar': False}),
                        type="cube", color=COLORS['accent']
                    )
                ], style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '20px', 'width': '65%'}),
                
                html.Div([
                    mirror_card
                ], style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '25px', 'width': '32%'})
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
            
            # Gráfico de impacto
            html.Div([
                dcc.Loading(
                    dcc.Graph(figure=impact_chart, config={'displayModeBar': False}),
                    type="cube", color=COLORS['accent']
                )
            ], style={'backgroundColor': COLORS['card'], 'borderRadius': '15px', 'padding': '20px', 'marginBottom': '30px'}),
            
            # Explicación metodológica
            html.Div([
                html.H4("🔬 Metodología: Estrategia del Espejo", 
                        style={'color': COLORS['text'], 'marginBottom': '15px'}),
                html.P([
                    "El ",
                    html.Strong("escenario sintético", style={'color': '#ef553b'}),
                    " se construye como una combinación ponderada de países que históricamente se comportaban de manera similar a ",
                    html.Strong(country_name, style={'color': COLORS['accent']}),
                    f" antes del año {event_year}. La diferencia entre ambas líneas representa el ",
                    html.Strong("impacto causal real", style={'color': impact_color}),
                    " del evento analizado."
                ], style={'color': COLORS['text_muted'], 'fontSize': '1rem', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                html.P([
                    "📌 ",
                    html.Strong("Transformación de datos:", style={'color': COLORS['text']}),
                    " Se utiliza PIB per Cápita en lugar de PIB absoluto para hacer comparables países de diferentes tamaños. ",
                    "Los países espejo se seleccionan mediante optimización matemática minimizando el error cuadrático en el período pre-evento."
                ], style={'color': COLORS['text_muted'], 'fontSize': '0.95rem', 'lineHeight': '1.6'})
            ], style={
                'backgroundColor': 'rgba(59, 130, 246, 0.08)',
                'borderRadius': '15px',
                'padding': '25px',
                'borderLeft': f'4px solid {COLORS["accent"]}'
            })
        ])
        
    except Exception as e:
        return html.Div([
            html.P(f"❌ Error durante el análisis: {str(e)}", 
                   style={'color': '#ef553b', 'textAlign': 'center', 'fontSize': '1rem', 'marginTop': '50px'}),
            html.P("Por favor, intenta con otra configuración o contacta soporte técnico.", 
                   style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '0.9rem', 'marginTop': '15px'})
        ])

if __name__ == '__main__':
    app.run(debug=True, port=8051)
