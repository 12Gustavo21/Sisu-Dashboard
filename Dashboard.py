from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

df_sisu = pd.read_csv('SISU2023.CSV', sep=';', decimal=',')

expected_columns = ['NO_CURSO', 'SG_UF_IES', 'SG_IES', 'QT_VAGAS_CONCORRENCIA', 'NU_NOTACORTE_CONCORRIDA']
if not set(expected_columns).issubset(df_sisu.columns):
    raise ValueError(f"As colunas esperadas ({expected_columns}) não estão presentes nos dados.")

cursos = df_sisu['NO_CURSO'].unique()
cursos.sort()

estados = df_sisu['SG_UF_IES'].unique()
estados.sort()

instituicoes = df_sisu['SG_IES'].unique()
instituicoes.sort()

app = Dash(__name__)

app.layout = html.Div([
    html.Header(
        children=[
            html.Div(
                className="logo-container",
                children=[
                    html.Img(src=app.get_asset_url("logo-sisu.svg")),
                ]
            ),
            html.H1(
                className="header-title",
                children='Dados do SISU 2023.1'
            ),
        ]
    ),

    html.Div(
        className="app-container",
        children=[
            html.Div(
                className="curso-container",
                children=[
                    html.H4(children='Cursos:'),
                    dcc.Dropdown(options=[{'label': curso, 'value': curso} for curso in cursos], id='dropdown-cursos', multi=True, placeholder='Selecione um curso...')
                ]),
            html.Div(
                className="estado-container",
                children=[
                    html.H4(children='Estados:'),
                    dcc.Dropdown(options=[{'label': estado, 'value': estado} for estado in estados], id='dropdown-estados', multi=True, placeholder='Selecione um estado...'),
                ]),

            html.Div(
                className="instituicao-container",
                children=[
                    html.H4(children='Instituições:'),
                    dcc.Dropdown(options=[{'label': instituicao, 'value': instituicao} for instituicao in instituicoes], id='dropdown-ies', multi=True, placeholder='Selecione uma instituição...')
                ]),

            html.Div(
                children=[
                    html.H4(
                        className="vagas-container",
                        children='Total de vagas', id="numero_vagas"),
                ]),

        ]),

    dcc.Graph(id='graph-vagas-estado'),
    dcc.Graph(id='graph-notas-estado'),
    dcc.Graph(id='graph-notas-ies'),
])


@app.callback(
    [Output('graph-vagas-estado', 'figure'),
     Output('graph-notas-estado', 'figure'),
     Output('graph-notas-ies', 'figure'),
     Output('numero_vagas', 'children')],
    [Input('dropdown-cursos', 'value'),
     Input('dropdown-estados', 'value'),
     Input('dropdown-ies', 'value')]
)
def update_graph(selected_cursos, selected_estados, selected_ies):
    if not selected_cursos or not selected_estados:
        return px.bar(), px.bar(), px.bar(), "Total de Vagas: 0"

    selected_cursos = [selected_cursos] if isinstance(selected_cursos, str) else selected_cursos
    selected_estados = [selected_estados] if isinstance(selected_estados, str) else selected_estados

    # Check if selected_ies is not None before using it in isin()
    if selected_ies is not None:
        selected_ies = [selected_ies] if isinstance(selected_ies, str) else selected_ies
        dff = df_sisu[
            (df_sisu['NO_CURSO'].isin(selected_cursos)) &
            (df_sisu['SG_UF_IES'].isin(selected_estados)) &
            (df_sisu['SG_IES'].isin(selected_ies))
        ]
    else:
        dff = df_sisu[
            (df_sisu['NO_CURSO'].isin(selected_cursos)) &
            (df_sisu['SG_UF_IES'].isin(selected_estados))
        ]

    if dff.empty:
        return px.bar(), px.bar(), px.bar(), "Total de Vagas: 0"

    numero_vagas = dff.shape[0]

    dff_vagas = dff.groupby('SG_UF_IES').count().reset_index()
    graph1 = px.bar(dff_vagas, x='SG_UF_IES', y='QT_VAGAS_CONCORRENCIA')
    graph1.update_xaxes(title_text='Estados')
    graph1.update_yaxes(title_text='Vagas')
    graph1.update_traces(hovertemplate='Estado: %{x}<br>Vagas: %{y}')
    graph1.update_layout(
        plot_bgcolor="#333333",
        paper_bgcolor="#212121",
        font_color="#fff",
        hoverlabel=dict(
            bgcolor="#333333",
            font_color="#fff"
        )
    )

    dff_nota = dff.groupby('SG_UF_IES').max().reset_index()
    graph2 = px.bar(dff_nota, x='SG_UF_IES', y='NU_NOTACORTE_CONCORRIDA')
    graph2.update_xaxes(title_text='Estados')
    graph2.update_yaxes(title_text='Notas')
    graph2.update_traces(hovertemplate='Estado: %{x}<br>Nota: %{y}')
    graph2.update_layout(
        plot_bgcolor="#333333",
        paper_bgcolor="#212121",
        font_color="#fff",
        hoverlabel=dict(
            bgcolor="#333333",
            font_color="#fff"
        )
    )

    dff_nota_ies = dff.groupby('SG_IES').max().reset_index()
    graph3 = px.bar(dff_nota_ies, x='SG_IES', y='NU_NOTACORTE_CONCORRIDA')
    graph3.update_xaxes(title_text='Instituições')
    graph3.update_yaxes(title_text='Notas')
    graph3.update_traces(hovertemplate='Instituição: %{x}<br>Nota: %{y}')
    graph3.update_layout(
        plot_bgcolor="#333333",
        paper_bgcolor="#212121",
        font_color="#fff",
        hoverlabel=dict(
            bgcolor="#333333",
            font_color="#fff"
        )
    )

    return graph1, graph2, graph3, f'Total de Vagas: {numero_vagas}'

if __name__ == '__main__':
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run_server(debug=True)