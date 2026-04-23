import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os

# ─── APP ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="Jenifer Gonzalez | Portfolio",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # necesario para Render

# ─── COLORES ───────────────────────────────────────────────────────────────────
C = {
    "bg":       "#0a0a0f",
    "bg2":      "#0f1117",
    "surface":  "#161b22",
    "surface2": "#1c2128",
    "border":   "#30363d",
    "border2":  "#21262d",
    "text":     "#e0e0e0",
    "muted":    "#8b949e",
    "blue":     "#58a6ff",
    "orange":   "#f97316",
    "ds":       "#3b82f6",
    "green":    "#22c55e",
    "red":      "#ef4444",
    "purple":   "#a855f7",
}

# ─── HELPERS CSS ───────────────────────────────────────────────────────────────


def badge(text):
    return html.Span(text, style={
        "display": "inline-block",
        "background": C["border2"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "6px",
        "padding": "2px 10px",
        "margin": "3px",
        "fontSize": "12px",
        "fontFamily": "Space Mono, monospace",
        "color": C["muted"],
    })


def card(children, accent=None, style_extra=None):
    style = {
        "background": f"linear-gradient(135deg, {C['surface']} 0%, {C['surface2']} 100%)",
        "border": f"1px solid {C['border']}",
        "borderRadius": "12px",
        "padding": "20px 24px",
        "margin": "10px 0",
        "transition": "border-color 0.3s",
    }
    if accent:
        style["borderLeft"] = f"4px solid {accent}"
    if style_extra:
        style.update(style_extra)
    return html.Div(children, style=style)


def check(text):
    return html.Div(f"✅ {text}", style={"fontSize": "13px", "color": C["muted"], "marginBottom": "6px"})


def metric_box(num, label):
    return html.Div([
        html.Div(num, style={"fontFamily": "Space Mono, monospace", "fontSize": "2rem",
                             "fontWeight": "700", "color": C["blue"]}),
        html.Div(label, style={"fontSize": "11px", "color": C["muted"],
                               "textTransform": "uppercase", "letterSpacing": "1px"}),
    ], style={
        "background": C["surface"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "10px",
        "padding": "16px",
        "textAlign": "center",
        "flex": "1",
        "minWidth": "100px",
    })


def tag(text, color):
    return html.Span(text, style={
        "background": f"{color}22",
        "border": f"1px solid {color}",
        "color": color,
        "borderRadius": "20px",
        "padding": "4px 14px",
        "fontSize": "12px",
        "fontFamily": "Space Mono, monospace",
    })


def gh_button(label, url):
    return html.A(label, href=url, target="_blank", style={
        "display": "block",
        "textAlign": "center",
        "background": C["border2"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "8px",
        "padding": "10px",
        "color": C["text"],
        "textDecoration": "none",
        "fontSize": "13px",
        "fontFamily": "Space Mono, monospace",
        "marginTop": "12px",
        "transition": "border-color 0.2s",
    })


def timeline_item(color, year, title, desc):
    return html.Div([
        html.Div(year, style={"fontSize": "11px", "color": color,
                              "fontFamily": "Space Mono, monospace", "letterSpacing": "1px"}),
        html.Div(title, style={"fontSize": "14px", "color": C["text"],
                               "fontWeight": "600", "margin": "4px 0"}),
        html.Div(desc, style={"fontSize": "13px",
                 "color": C["muted"], "lineHeight": "1.6"}),
    ], style={
        "borderLeft": f"3px solid {color}",
        "paddingLeft": "16px",
        "marginBottom": "20px",
    })


# ─── FIGURAS ESTÁTICAS (se generan una vez) ────────────────────────────────────
PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color=C["muted"],
    margin=dict(t=20, b=20, l=10, r=10),
    height=280,
)


def fig_qa_dashboard():
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    rates = [100, 95, 90, 88, 92]
    colors = [C["green"] if r == 100 else C["orange"]
              if r < 92 else C["ds"] for r in rates]
    fig = go.Figure(go.Bar(
        x=methods, y=rates,
        marker_color=colors,
        text=[f"{r}%" for r in rates],
        textposition="outside",
    ))
    fig.update_layout(**PLOT_LAYOUT,
                      showlegend=False,
                      yaxis=dict(range=[80, 105], gridcolor=C["border2"]),
                      xaxis=dict(gridcolor=C["border2"]),
                      )
    return fig


def fig_api_coverage():
    endpoints = ["GET /posts", "POST /posts", "PUT /{id}", "PATCH /{id}",
                 "DELETE /{id}", "GET /users", "GET /comments", "GET /todos"]
    passed = [5, 3, 2, 2, 2, 4, 3, 3]
    failed = [0, 1, 0, 0, 0, 0, 0, 0]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Passed", x=endpoints,
                  y=passed, marker_color=C["green"]))
    fig.add_trace(go.Bar(name="Failed", x=endpoints,
                  y=failed, marker_color=C["red"]))
    fig.update_layout(**PLOT_LAYOUT,
                      barmode="stack",
                      legend=dict(bgcolor="rgba(0,0,0,0)"),
                      xaxis=dict(tickangle=-30, gridcolor=C["border2"]),
                      yaxis=dict(gridcolor=C["border2"]),
                      )
    return fig


def fig_cicd_pie():
    fig = go.Figure(go.Pie(
        labels=["Smoke", "Regression", "Performance"],
        values=[17, 28, 6],
        hole=0.6,
        marker_colors=[C["orange"], C["ds"], C["purple"]],
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig.update_layout(**PLOT_LAYOUT,
                      showlegend=False,
                      annotations=[dict(text="51 tests", x=0.5, y=0.5,
                                        font_size=16, font_color=C["text"], showarrow=False)],
                      )
    return fig


def fig_age_histogram():
    np.random.seed(0)
    ages = np.concatenate([
        np.random.normal(25, 5, 300),
        np.random.normal(40, 8, 400),
        np.random.normal(60, 7, 200),
    ])
    ages = np.clip(ages, 1, 80).astype(int)
    fig = px.histogram(x=ages, nbins=40, color_discrete_sequence=[C["ds"]])
    fig.update_layout(**PLOT_LAYOUT,
                      xaxis=dict(gridcolor=C["border2"], title="Edad"),
                      yaxis=dict(gridcolor=C["border2"], title="Frecuencia"),
                      bargap=0.05,
                      )
    return fig


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
sidebar = html.Div([
    # Banner o header
    html.Div([
        html.Img(src="/assets/banner.png",
                 style={"width": "100%", "borderRadius": "8px"})
        if os.path.exists("assets/banner.png") else
        html.Div([
            html.Div("Jenifer Gonzalez", style={
                "fontFamily": "Space Mono, monospace", "fontSize": "17px",
                "fontWeight": "700", "color": C["text"], "lineHeight": "1.3",
            }),
            html.Div("QA Automation", style={
                     "fontSize": "11px", "color": C["muted"], "marginTop": "6px"}),
            html.Div("→ Data Science", style={
                     "fontSize": "11px", "color": C["blue"]}),
        ], style={"textAlign": "center", "padding": "20px 0 10px"}),
    ]),

    html.Hr(style={"borderColor": C["border"], "margin": "12px 0"}),

    # Navegación
    html.P("NAVEGACIÓN", style={
        "fontSize": "10px", "color": C["muted"], "letterSpacing": "2px",
        "fontFamily": "Space Mono, monospace", "margin": "8px 0",
    }),

    html.Div([
        html.Button(label, id=f"nav-{key}", n_clicks=0, style={
            "width": "100%", "textAlign": "left",
            "background": C["border2"], "color": C["text"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "8px", "padding": "10px 14px",
            "marginBottom": "6px", "cursor": "pointer",
            "fontFamily": "Space Mono, monospace", "fontSize": "13px",
            "transition": "all 0.2s",
        })
        for key, label in [
            ("home",     "🏠  Inicio"),
            ("qa",       "🧪  Mundo QA"),
            ("ds",       "📊  Mundo Data Science"),
            ("about",    "👩‍💻  Sobre mí"),
        ]
    ]),

    html.Hr(style={"borderColor": C["border"], "margin": "12px 0"}),

    # Links
    html.Div([
        html.A("🔗 LinkedIn", href="https://www.linkedin.com/in/jenifer-paola-gonzalez-pe%C3%B1uela/",
               target="_blank", style={"color": C["blue"], "textDecoration": "none",
                                       "fontSize": "12px", "display": "block", "marginBottom": "8px"}),
        html.A("🐙 GitHub", href="https://github.com/Jenifer-Gonzalez-DS-QA",
               target="_blank", style={"color": C["blue"], "textDecoration": "none",
                                       "fontSize": "12px", "display": "block"}),
    ], style={"padding": "6px 0"}),

    html.Div(style={"height": "16px"}),

    # Botón CV
    html.Div(id="cv-button-container"),

], style={
    "width": "240px",
    "minWidth": "240px",
    "background": f"linear-gradient(180deg, {C['bg2']} 0%, {C['surface']} 100%)",
    "borderRight": f"1px solid {C['border']}",
    "padding": "16px",
    "height": "100vh",
    "overflowY": "auto",
    "position": "sticky",
    "top": "0",
    "boxSizing": "border-box",
})

# ─── LAYOUT PRINCIPAL ──────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="current-page", data="home"),

    # CSS global
    html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
    html.Link(rel="stylesheet",
              href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap"),

    # Layout flex: sidebar + contenido
    html.Div([
        sidebar,
        html.Div(id="page-content", style={
            "flex": "1",
            "padding": "32px 40px",
            "overflowY": "auto",
            "height": "100vh",
            "boxSizing": "border-box",
        }),
    ], style={"display": "flex", "height": "100vh", "overflow": "hidden"}),

], style={
    "background": C["bg"],
    "color": C["text"],
    "fontFamily": "Inter, sans-serif",
    "margin": "0",
    "padding": "0",
})

# ─── PÁGINAS ───────────────────────────────────────────────────────────────────


def page_home():
    return html.Div([
        # Hero
        html.Div([
            html.Div("BIENVENIDO A MI PORTAFOLIO", style={
                "fontFamily": "Space Mono, monospace", "fontSize": "12px",
                "color": C["muted"], "letterSpacing": "3px", "marginBottom": "16px",
            }),
            html.H1("Jenifer Gonzalez", style={
                "fontSize": "3rem", "margin": "0",
                "background": f"linear-gradient(90deg, {C['orange']}, {C['ds']})",
                "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
                "fontFamily": "Space Mono, monospace",
            }),
            html.Div("QA Automation Engineer  →  Data Scientist", style={
                "fontFamily": "Space Mono, monospace", "fontSize": "1rem",
                "color": C["muted"], "margin": "12px 0 24px",
            }),
            html.P(
                "Ingeniera de Sistemas con experiencia en aseguramiento de calidad y metodologías "
                "ágiles, en transición activa hacia la Ciencia de Datos. Combino la mentalidad QA "
                "—rigor, trazabilidad, confiabilidad— con análisis y modelos predictivos de impacto real.",
                style={"maxWidth": "600px", "margin": "0 auto", "color": C["muted"],
                       "fontSize": "15px", "lineHeight": "1.7"},
            ),
        ], style={"textAlign": "center", "padding": "20px 0 32px"}),

        # Cards dos mundos
        html.Div([
            # QA Card
            card([
                html.Div("🧪", style={"fontSize": "3rem",
                         "marginBottom": "12px"}),
                html.Div("Mundo QA", style={
                    "fontFamily": "Space Mono, monospace", "fontSize": "1.2rem",
                    "color": C["orange"], "marginBottom": "8px",
                }),
                html.P("Frameworks de automatización, CI/CD con GitHub Actions, dashboards de "
                       "métricas de calidad en tiempo real. 3 proyectos que forman un ecosistema completo.",
                       style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.6"}),
                html.Div([badge("Pytest"), badge("GitHub Actions"), badge("Plotly")],
                         style={"marginTop": "12px"}),
                html.Button("🧪 Explorar Mundo QA", id="card-go-qa", n_clicks=0, style={
                    "marginTop": "16px", "width": "100%", "padding": "10px",
                    "background": f"{C['orange']}22", "border": f"1px solid {C['orange']}",
                    "color": C["orange"], "borderRadius": "8px", "cursor": "pointer",
                    "fontFamily": "Space Mono, monospace", "fontSize": "13px",
                }),
            ], accent=C["orange"], style_extra={"textAlign": "center", "flex": "1"}),

            html.Div(style={"width": "24px"}),

            # DS Card
            card([
                html.Div("📊", style={"fontSize": "3rem",
                         "marginBottom": "12px"}),
                html.Div("Mundo Data Science", style={
                    "fontFamily": "Space Mono, monospace", "fontSize": "1.2rem",
                    "color": C["ds"], "marginBottom": "8px",
                }),
                html.P("Machine Learning, Deep Learning y análisis predictivo aplicado a industria, "
                       "salud y telecomunicaciones. Modelos reales con impacto de negocio medible.",
                       style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.6"}),
                html.Div([badge("Scikit-learn"), badge("XGBoost"), badge("TensorFlow")],
                         style={"marginTop": "12px"}),
                html.Button("📊 Explorar Mundo DS", id="card-go-ds", n_clicks=0, style={
                    "marginTop": "16px", "width": "100%", "padding": "10px",
                    "background": f"{C['ds']}22", "border": f"1px solid {C['ds']}",
                    "color": C["ds"], "borderRadius": "8px", "cursor": "pointer",
                    "fontFamily": "Space Mono, monospace", "fontSize": "13px",
                }),
            ], accent=C["ds"], style_extra={"textAlign": "center", "flex": "1"}),

        ], style={"display": "flex", "gap": "0", "alignItems": "stretch"}),

        # Métricas
        html.Div("EN NÚMEROS", style={
            "fontFamily": "Space Mono, monospace", "fontSize": "10px", "color": C["muted"],
            "textTransform": "uppercase", "letterSpacing": "2px",
            "textAlign": "center", "margin": "32px 0 16px",
        }),
        html.Div([
            metric_box("6",  "Proyectos"),
            metric_box("3",  "QA Repos"),
            metric_box("3",  "DS Modelos"),
            metric_box("51", "Pruebas auto."),
            metric_box("3",  "Stacks tech"),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),
    ])


def page_qa():
    return html.Div([
        html.Div([
            tag("🧪 QA AUTOMATION", C["orange"]),
            html.H2("Ecosistema de Automatización",
                    style={"fontFamily": "Space Mono, monospace", "margin": "12px 0 4px"}),
            html.P("Tres proyectos diseñados para trabajar juntos: framework base → análisis de datos → CI/CD automático.",
                   style={"color": C["muted"], "fontSize": "14px"}),
        ], style={"marginBottom": "24px"}),

        # Tabs de proyecto
        html.Div([
            html.Button("📊 QA Dashboard",      id="qa-tab-0", n_clicks=0),
            html.Button("🔌 API Framework",      id="qa-tab-1", n_clicks=0),
            html.Button("🔄 CI/CD Pipeline",     id="qa-tab-2", n_clicks=0),
        ], id="qa-tabs", style={"display": "flex", "gap": "8px", "marginBottom": "24px",
                                "flexWrap": "wrap"}),

        html.Div(id="qa-content"),

        # Ecosistema
        card([
            html.Div("💡 Los 3 proyectos forman un ecosistema completo",
                     style={"fontFamily": "Space Mono, monospace", "fontSize": "13px",
                            "color": C["orange"], "marginBottom": "8px"}),
            html.Div([
                html.Span("🔌 API Testing Framework"),
                html.Span(" → ", style={"color": C["orange"]}),
                html.Span("📊 QA Dashboard"),
                html.Span(" → ", style={"color": C["orange"]}),
                html.Span("🔄 CI/CD Pipeline"),
            ], style={"fontSize": "13px", "color": C["muted"]}),
        ], style_extra={"background": f"{C['orange']}08", "borderColor": C["orange"],
                        "marginTop": "24px"}),
    ])


def page_ds():
    return html.Div([
        html.Div([
            tag("📊 DATA SCIENCE", C["ds"]),
            html.H2("Proyectos de Machine Learning",
                    style={"fontFamily": "Space Mono, monospace", "margin": "12px 0 4px"}),
            html.P("Modelos predictivos aplicados a industria pesada, visión por computadora y telecomunicaciones.",
                   style={"color": C["muted"], "fontSize": "14px"}),
        ], style={"marginBottom": "24px"}),

        html.Div([
            html.Button("🥇 Predicción Oro",     id="ds-tab-0", n_clicks=0),
            html.Button("👁 Verificación Edad",  id="ds-tab-1", n_clicks=0),
            html.Button("📱 Churn Telco",        id="ds-tab-2", n_clicks=0),
        ], id="ds-tabs", style={"display": "flex", "gap": "8px", "marginBottom": "24px",
                                "flexWrap": "wrap"}),

        html.Div(id="ds-content"),
    ])


def page_about():
    return html.Div([
        html.Div([
            # Col izquierda
            html.Div([
                card([
                    html.Div("👩‍💻", style={
                             "fontSize": "3rem", "marginBottom": "12px"}),
                    html.Div("Jenifer Gonzalez",
                             style={"fontFamily": "Space Mono, monospace", "fontSize": "1.1rem",
                                    "color": C["text"], "marginBottom": "6px"}),
                    html.Div("Bogotá, Colombia",
                             style={"fontSize": "12px", "color": C["muted"], "marginBottom": "16px"}),
                    html.Div([
                        html.Div(
                            r, style={"fontSize": "13px", "color": C["muted"], "lineHeight": "1.8"})
                        for r in ["Ingeniera de Sistemas", "QA Automation Engineer",
                                  "Scrum Master", "Data Scientist"]
                    ]),
                ], style_extra={"textAlign": "center"}),
                html.Div(style={"height": "16px"}),
                html.Div("Habilidades blandas", style={
                         "fontWeight": "600", "marginBottom": "8px"}),
                html.Div([
                    html.Div(f"→ {h}", style={"fontSize": "13px",
                             "color": C["muted"], "padding": "4px 0"})
                    for h in ["Pensamiento analítico", "Orientada a calidad",
                              "Trabajo en equipo ágil", "Comunicación técnica",
                              "Mentalidad de mejora continua", "Resolución de problemas"]
                ]),
            ], style={"flex": "1"}),

            html.Div(style={"width": "32px"}),

            # Col derecha
            html.Div([
                html.H4("Mi trayectoria", style={"fontFamily": "Space Mono, monospace",
                                                 "marginBottom": "20px"}),
                timeline_item(C["green"], "2024 – Hoy", "Bootcamp Data Science · TripleTen",
                              "ML, Deep Learning, NLP, Streamlit. Construcción de portafolio con proyectos reales."),
                timeline_item(C["ds"], "2023 – 2024", "QA Automation Engineer",
                              "Automatización con Python y Pytest. Integración CI/CD con GitHub Actions."),
                timeline_item(C["orange"], "2019 – 2023", "QA Manual + Scrum Master",
                              "Gestión de calidad en equipos ágiles. Liderazgo de ceremonias Scrum/Kanban."),
                timeline_item(C["muted"], "2019", "Ingeniería de Sistemas",
                              "Formación base en desarrollo de software, bases de datos y programación."),
                html.Div(style={"height": "16px"}),
                html.H4("Lo que busco", style={"fontFamily": "Space Mono, monospace",
                                               "marginBottom": "12px"}),
                card([
                    html.P("Un rol donde pueda conectar mi experiencia en QA y metodologías ágiles "
                           "con la Ciencia de Datos. Me interesa especialmente cualquier posición donde "
                           "los datos confiables y los procesos de calidad sean parte del mismo flujo.",
                           style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.7",
                                  "margin": "0 0 12px"}),
                    html.Div("Data Science · Data Analyst · Data Engineer · QA Data · Analytics Engineer",
                             style={"color": C["ds"], "fontSize": "13px"}),
                ], accent=C["ds"]),
            ], style={"flex": "1.2"}),

        ], style={"display": "flex", "alignItems": "flex-start"}),
    ])


# ─── CONTENIDO QA POR TAB ──────────────────────────────────────────────────────
def qa_tab_content(tab):
    projects = [
        {
            "title": "📊 QA Dashboard",
            "desc": ("Dashboard interactivo que combina automatización de pruebas de API con análisis "
                     "de datos. Ejecuta 22 tests contra una API REST, guarda resultados en CSV acumulativo "
                     "y genera visualizaciones Plotly en tiempo real. Un solo comando hace todo."),
            "badges": ["Python 3.11", "Pandas", "Plotly", "Requests"],
            "checks": ["22 pruebas CRUD automatizadas", "CSV acumulativo con timestamps",
                       "Dashboard HTML sin servidor", "KPIs + tendencia entre ejecuciones"],
            "url": "https://github.com/Jenifer-Gonzalez-DS-QA/qa-dashboard",
            "fig": fig_qa_dashboard(),
            "extras": html.Div([
                html.Div([
                    html.Div([html.Div("21", style={"fontFamily": "Space Mono,monospace", "fontSize": "1.5rem", "color": C["green"]}),
                              html.Div("Pasaron", style={"fontSize": "11px", "color": C["muted"]})],
                             style={"textAlign": "center", "flex": "1"}),
                    html.Div([html.Div("89ms", style={"fontFamily": "Space Mono,monospace", "fontSize": "1.5rem", "color": C["blue"]}),
                              html.Div("Promedio", style={"fontSize": "11px", "color": C["muted"]})],
                             style={"textAlign": "center", "flex": "1"}),
                    html.Div([html.Div("95.5%", style={"fontFamily": "Space Mono,monospace", "fontSize": "1.5rem", "color": C["orange"]}),
                              html.Div("Éxito", style={"fontSize": "11px", "color": C["muted"]})],
                             style={"textAlign": "center", "flex": "1"}),
                ], style={"display": "flex", "gap": "8px", "marginTop": "12px"}),
            ]),
        },
        {
            "title": "🔌 API Testing Framework",
            "desc": ("Framework profesional de automatización de pruebas para APIs REST. Cubre operaciones "
                     "CRUD completas sobre usuarios, posts, comentarios y todos con reportes HTML automáticos."),
            "badges": ["Python", "Pytest", "Requests", "pytest-html"],
            "checks": ["CRUD sobre 4 endpoints", "Reportes HTML auto-generados",
                       "Fixtures y conftest reutilizables", "Sin dependencia de credenciales externas"],
            "url": "https://github.com/Jenifer-Gonzalez-DS-QA/api-testing-framework",
            "fig": fig_api_coverage(),
            "extras": None,
        },
        {
            "title": "🔄 QA CI/CD Pipeline",
            "desc": ("Suite de pruebas con 3 niveles integrada con GitHub Actions. Las pruebas corren "
                     "automáticamente en cada push, PR y de lunes a viernes a las 8am."),
            "badges": ["Pytest", "GitHub Actions", "pytest-html", "YAML"],
            "checks": ["17 pruebas Smoke (críticas)", "28 pruebas de Regresión",
                       "6 pruebas de Performance (<3s)", "Artifacts HTML por 30 días"],
            "url": "https://github.com/Jenifer-Gonzalez-DS-QA/qa-cicd-pipeline",
            "fig": fig_cicd_pie(),
            "extras": html.Div(
                "⚡ Se activa en cada push y pull request automáticamente",
                style={"fontSize": "12px",
                       "color": C["muted"], "textAlign": "center", "marginTop": "8px"},
            ),
        },
    ]
    p = projects[tab]
    return html.Div([
        html.Div([
            # Info
            html.Div([
                card([
                    html.Div(p["title"], style={"fontFamily": "Space Mono, monospace",
                                                "fontSize": "1.1rem", "color": C["orange"],
                                                "marginBottom": "8px"}),
                    html.P(p["desc"], style={"color": C["muted"], "fontSize": "14px",
                                             "lineHeight": "1.7"}),
                    html.Div([badge(b) for b in p["badges"]],
                             style={"margin": "12px 0"}),
                    html.Div([check(c) for c in p["checks"]]),
                    gh_button("🔗 Ver repositorio en GitHub", p["url"]),
                ], accent=C["orange"]),
            ], style={"flex": "1.2"}),

            html.Div(style={"width": "24px"}),

            # Demo
            html.Div([
                html.Div("Demo interactiva", style={
                         "fontWeight": "600", "marginBottom": "12px"}),
                dcc.Graph(figure=p["fig"], config=PLOT_CONFIG),
                p["extras"] if p["extras"] else html.Div(),
            ], style={"flex": "1"}),

        ], style={"display": "flex", "alignItems": "flex-start"}),
    ])


# ─── CONTENIDO DS POR TAB ──────────────────────────────────────────────────────
def ds_tab_content(tab):
    if tab == 0:
        return html.Div([
            html.Div([
                html.Div([
                    card([
                        html.Div("🥇 Predicción de Recuperación de Oro",
                                 style={"fontFamily": "Space Mono,monospace", "fontSize": "1.1rem",
                                        "color": C["ds"], "marginBottom": "8px"}),
                        html.Div("Industria pesada · Regresión · Optimización de procesos",
                                 style={"fontSize": "12px", "color": C["muted"], "marginBottom": "10px"}),
                        html.P("Modelo de ML para predecir la cantidad de oro extraído del mineral en etapas "
                               "de flotación y purificación. Ayuda a optimizar la producción e identificar "
                               "parámetros no rentables en el proceso industrial.",
                               style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.7"}),
                        html.Div([badge(b) for b in ["XGBoost", "Scikit-learn", "Pandas", "sMAPE"]],
                                 style={"margin": "12px 0"}),
                        html.Div([check(c) for c in [
                            "EDA de proceso industrial minero",
                            "Ingeniería de características sobre etapas",
                            "Métrica personalizada sMAPE ponderado",
                            "Comparación RandomForest vs XGBoost vs baseline",
                        ]]),
                        gh_button("🔗 Ver repositorio en GitHub",
                                  "https://github.com/Jenifer-Gonzalez-DS-QA/Prediccion-de-recuperacion-de-oro"),
                    ], accent=C["ds"]),
                ], style={"flex": "1.2"}),

                html.Div(style={"width": "24px"}),

                # Demo interactiva con sliders
                html.Div([
                    html.Div("Demo: Simula predicción de recuperación",
                             style={"fontWeight": "600", "marginBottom": "16px"}),
                    html.Div("Reactivo flotación (xanthate)",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(1, 15, 0.1, value=7.5, id="gold-reagent",
                               marks={1: "1", 15: "15"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Div("Densidad del pulp (%)",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(20, 60, 0.5, value=40, id="gold-density",
                               marks={20: "20%", 60: "60%"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Div("Alimentación de aire",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(500, 1500, 10, value=900, id="gold-air",
                               marks={500: "500", 1500: "1500"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "20px"}),
                    html.Div(id="gold-result"),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "alignItems": "flex-start"}),
        ])

    elif tab == 1:
        return html.Div([
            html.Div([
                html.Div([
                    card([
                        html.Div("👁 Verificación de Edad con Deep Learning",
                                 style={"fontFamily": "Space Mono,monospace", "fontSize": "1.1rem",
                                        "color": C["ds"], "marginBottom": "8px"}),
                        html.Div("Computer Vision · Deep Learning · Clasificación",
                                 style={"fontSize": "12px", "color": C["muted"], "marginBottom": "10px"}),
                        html.P("Modelo de aprendizaje profundo para estimar la edad de personas a partir de "
                               "fotografías faciales. Aplicación directa en retail para verificación de edad "
                               "en la compra de productos regulados.",
                               style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.7"}),
                        html.Div([badge(b) for b in ["TensorFlow", "ResNet50", "Keras", "MAE"]],
                                 style={"margin": "12px 0"}),
                        html.Div([check(c) for c in [
                            "Transfer learning con ResNet50",
                            "Data augmentation aplicado",
                            "Evaluación con MAE",
                            "Aplicación en control de ventas reguladas",
                        ]]),
                        gh_button("🔗 Ver repositorio en GitHub",
                                  "https://github.com/Jenifer-Gonzalez-DS-QA/Verificacion_de_Edad"),
                    ], accent=C["ds"]),
                ], style={"flex": "1.2"}),
                html.Div(style={"width": "24px"}),
                html.Div([
                    html.Div("Distribución de edades en dataset",
                             style={"fontWeight": "600", "marginBottom": "12px"}),
                    dcc.Graph(figure=fig_age_histogram(), config=PLOT_CONFIG),
                    html.Div([
                        html.Div("~7.2 años", style={"fontFamily": "Space Mono,monospace",
                                                     "fontSize": "1.5rem", "color": C["ds"]}),
                        html.Div("MAE del modelo", style={
                                 "fontSize": "11px", "color": C["muted"]}),
                    ], style={"textAlign": "center", "marginTop": "8px"}),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "alignItems": "flex-start"}),
        ])

    else:  # tab == 2
        return html.Div([
            html.Div([
                html.Div([
                    card([
                        html.Div("📱 Churn en Telecomunicaciones",
                                 style={"fontFamily": "Space Mono,monospace", "fontSize": "1.1rem",
                                        "color": C["ds"], "marginBottom": "8px"}),
                        html.Div("Clasificación · Retención de clientes · Negocio",
                                 style={"fontSize": "12px", "color": C["muted"], "marginBottom": "10px"}),
                        html.P("Modelo predictivo para identificar clientes en riesgo de cancelación (churn). "
                               "Permite acciones preventivas de retención antes de que el cliente se vaya.",
                               style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.7"}),
                        html.Div([badge(b) for b in ["LightGBM", "Scikit-learn", "Pandas", "ROC-AUC"]],
                                 style={"margin": "12px 0"}),
                        html.Div([check(c) for c in [
                            "Análisis de features de comportamiento",
                            "Manejo de desbalance de clases",
                            "Optimización de umbral de decisión",
                            "Feature importance interpretable",
                        ]]),
                        gh_button("🔗 Ver repositorio en GitHub",
                                  "https://github.com/Jenifer-Gonzalez-DS-QA/Proyecto_Telecomunicaciones"),
                    ], accent=C["ds"]),
                ], style={"flex": "1.2"}),
                html.Div(style={"width": "24px"}),
                html.Div([
                    html.Div("Demo: Predicción de riesgo de churn",
                             style={"fontWeight": "600", "marginBottom": "16px"}),
                    html.Div("Meses como cliente",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(1, 72, 1, value=12, id="churn-antiguedad",
                               marks={1: "1", 72: "72"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Div("Llamadas a soporte (último mes)",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(0, 10, 1, value=2, id="churn-llamadas",
                               marks={0: "0", 10: "10"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Div("Cargo mensual (USD)",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "4px"}),
                    dcc.Slider(20, 120, 0.5, value=65, id="churn-cargo",
                               marks={20: "$20", 120: "$120"}, tooltip={"always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Div("Tipo de contrato",
                             style={"fontSize": "13px", "color": C["muted"], "marginBottom": "8px"}),
                    dcc.RadioItems(
                        ["Mensual", "1 año", "2 años"], "Mensual",
                        id="churn-contrato",
                        inline=True,
                        style={"color": C["muted"], "fontSize": "13px"},
                    ),
                    html.Div(style={"height": "20px"}),
                    html.Div(id="churn-result"),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "alignItems": "flex-start"}),
        ])


# ─── ESTILOS TABS ──────────────────────────────────────────────────────────────
TAB_ACTIVE = {
    "background": C["border2"], "color": C["text"],
    "border": f"1px solid {C['blue']}", "borderRadius": "8px",
    "padding": "8px 16px", "cursor": "pointer",
    "fontFamily": "Space Mono, monospace", "fontSize": "12px",
}
TAB_INACTIVE = {
    "background": "transparent", "color": C["muted"],
    "border": f"1px solid {C['border']}", "borderRadius": "8px",
    "padding": "8px 16px", "cursor": "pointer",
    "fontFamily": "Space Mono, monospace", "fontSize": "12px",
}

# ─── CALLBACKS ─────────────────────────────────────────────────────────────────

# Navegación principal


@app.callback(
    Output("current-page", "data"),
    [Input("nav-home", "n_clicks"), Input("nav-qa", "n_clicks"),
     Input("nav-ds", "n_clicks"),  Input("nav-about", "n_clicks"),
     Input("card-go-qa", "n_clicks"), Input("card-go-ds", "n_clicks")],
    prevent_initial_call=True,
)
def navigate(*args):
    ctx = callback_context
    if not ctx.triggered:
        return "home"
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    mapping = {
        "nav-home": "home", "nav-qa": "qa", "nav-ds": "ds", "nav-about": "about",
        "card-go-qa": "qa", "card-go-ds": "ds",
    }
    return mapping.get(btn, "home")

# Renderizar página


@app.callback(Output("page-content", "children"), Input("current-page", "data"))
def render_page(page):
    pages = {"home": page_home, "qa": page_qa,
             "ds": page_ds, "about": page_about}
    return pages.get(page, page_home)()

# CV download


@app.callback(Output("cv-button-container", "children"), Input("current-page", "data"))
def render_cv(_):
    for name in ["Jenifer_Gonzalez_CV.pdf", "cv.pdf", "CV.pdf", "assets/cv.pdf"]:
        if os.path.exists(name):
            return html.A("📄  Descargar CV", href=f"/assets/{name.split('/')[-1]}",
                          download=name.split("/")[-1], style={
                              "display": "block", "textAlign": "center",
                              "background": C["border2"], "border": f"1px solid {C['border']}",
                              "borderRadius": "8px", "padding": "10px",
                              "color": C["text"], "textDecoration": "none",
                              "fontSize": "12px", "fontFamily": "Space Mono, monospace",
            })
    return html.Div("📄 CV — próximamente", style={
        "background": C["border2"], "border": f"1px dashed {C['border']}",
        "borderRadius": "8px", "padding": "10px", "textAlign": "center",
        "fontSize": "12px", "color": C["muted"], "fontFamily": "Space Mono, monospace",
    })

# QA tabs


@app.callback(
    Output("qa-content", "children"),
    [Input("qa-tab-0", "n_clicks"), Input("qa-tab-1",
                                          "n_clicks"), Input("qa-tab-2", "n_clicks")],
    prevent_initial_call=False,
)
def qa_content(t0, t1, t2):
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]["prop_id"] == ".":
        return qa_tab_content(0)
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    return qa_tab_content({"qa-tab-0": 0, "qa-tab-1": 1, "qa-tab-2": 2}.get(btn, 0))

# DS tabs


@app.callback(
    Output("ds-content", "children"),
    [Input("ds-tab-0", "n_clicks"), Input("ds-tab-1",
                                          "n_clicks"), Input("ds-tab-2", "n_clicks")],
    prevent_initial_call=False,
)
def ds_content(t0, t1, t2):
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]["prop_id"] == ".":
        return ds_tab_content(0)
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    return ds_tab_content({"ds-tab-0": 0, "ds-tab-1": 1, "ds-tab-2": 2}.get(btn, 0))

# Demo Oro


@app.callback(
    Output("gold-result", "children"),
    [Input("gold-reagent", "value"), Input("gold-density",
                                           "value"), Input("gold-air", "value")],
)
def gold_prediction(reagent, density, air):
    pred = 65 + (reagent - 7.5)*2.1 + (density - 40)*0.3 + (air - 900)*0.01
    pred = max(40, min(95, pred))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pred,
        number={"suffix": "%", "font": {"color": C["text"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": C["muted"]},
            "bar": {"color": C["ds"]},
            "steps": [{"range": [0, 100], "color": C["surface"]}],
            "threshold": {"line": {"color": C["green"], "width": 3}, "value": 75},
            "bgcolor": C["surface"],
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=C["muted"],
                      height=200, margin=dict(t=20, b=10, l=10, r=10))
    label = "Buena recuperación ✅" if pred > 70 else "Optimizar parámetros ⚠️"
    return html.Div([
        html.Div(f"{pred:.1f}% — {label}", style={
            "fontFamily": "Space Mono,monospace", "fontSize": "14px",
            "color": C["green"] if pred > 70 else C["orange"],
            "textAlign": "center", "marginBottom": "8px",
        }),
        dcc.Graph(figure=fig, config=PLOT_CONFIG),
    ])

# Demo Churn


@app.callback(
    Output("churn-result", "children"),
    [Input("churn-antiguedad", "value"), Input("churn-llamadas", "value"),
     Input("churn-cargo", "value"),     Input("churn-contrato", "value")],
)
def churn_prediction(antiguedad, llamadas, cargo, contrato):
    score = 0.4
    score -= antiguedad * 0.005
    score += llamadas * 0.07
    score += (cargo - 65) * 0.002
    if contrato == "Mensual":
        score += 0.2
    elif contrato == "2 años":
        score -= 0.25
    score = max(0.02, min(0.98, score))

    color = C["red"] if score > 0.6 else C["orange"] if score > 0.35 else C["green"]
    label = "⚠️ ALTO RIESGO" if score > 0.6 else "⚡ RIESGO MEDIO" if score > 0.35 else "✅ BAJO RIESGO"

    return html.Div([
        html.Div(f"{score*100:.0f}%", style={
            "fontFamily": "Space Mono,monospace", "fontSize": "2.5rem",
            "fontWeight": "700", "color": color, "textAlign": "center",
        }),
        html.Div(label, style={"fontSize": "13px",
                 "color": color, "textAlign": "center"}),
        html.Div("Probabilidad de cancelación en los próximos 30 días",
                 style={"fontSize": "11px", "color": C["muted"], "textAlign": "center", "marginTop": "6px"}),
    ], style={
        "background": C["surface"], "border": f"2px solid {color}",
        "borderRadius": "10px", "padding": "16px", "marginTop": "8px",
    })


# ─── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 8050)))
