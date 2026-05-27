import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Configuracoes Globais e Cyberpunk
st.set_page_config(page_title="Steam Market Intelligence", layout="wide", page_icon="🎮", initial_sidebar_state="collapsed")

# Forca o tema dark nos graficos
pio.templates.default = "plotly_dark"

# Paleta Cyberpunk
CYBER_CYAN = '#00FFFF'
CYBER_MAGENTA = '#FF00FF'
CYBER_YELLOW = '#FFFF00'
CYBER_BG = '#0B0B1A'

# Estilizacao Cyberpunk Pesada via CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* Fundo Geral da Pagina */
[data-testid="stAppViewContainer"] {
    background-color: #05050A;
    background-image: 
        linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 30px 30px;
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    color: #E0E0E0;
}

/* Cabeçalhos H1, H2, H3 */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif !important;
    color: #FFFFFF !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}
h1 { text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF !important; }
h2 { text-shadow: 0 0 8px #FF00FF !important; }
h3 { text-shadow: 0 0 5px #FFFF00 !important; color: #FFFF00 !important; }

/* Linhas horizontais (---) */
hr {
    border-color: #FF00FF !important;
    box-shadow: 0 0 10px #FF00FF;
    opacity: 0.5;
}

/* Caixas de Insight (Neon) */
.insight-box {
    background: rgba(10, 10, 20, 0.85) !important;
    padding: 25px;
    border-radius: 0px;
    border: 1px solid #FF00FF;
    border-left: 6px solid #00FFFF;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(255, 0, 255, 0.1);
    color: #E0E0E0;
    font-size: 17px;
    margin-top: 15px;
    backdrop-filter: blur(4px);
    font-family: 'Rajdhani', sans-serif;
    line-height: 1.5;
}

.insight-title {
    color: #00FFFF;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    margin-bottom: 15px;
    font-size: 18px;
    text-shadow: 0 0 5px #00FFFF;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Botoes das Abas (Cyberpunk Buttons) */
button[data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 15px 30px !important;
    background-color: transparent !important;
    color: #00FFFF !important;
    border: 2px solid #00FFFF !important;
    border-radius: 0px !important;
    margin-right: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 5px #00FFFF !important;
    text-transform: uppercase;
}

button[data-baseweb="tab"] p {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: inherit !important;
}

button[data-baseweb="tab"]:focus, button[data-baseweb="tab"]:active, button[aria-selected="true"] {
    background-color: rgba(0, 255, 255, 0.2) !important;
    box-shadow: 0 0 15px #00FFFF, inset 0 0 10px #00FFFF !important;
    color: #FFFFFF !important;
    border-color: #FFFFFF !important;
}

/* KPIs (Metrics) */
[data-testid="stMetricValue"] {
    color: #FF00FF !important;
    font-family: 'Orbitron', sans-serif !important;
    text-shadow: 0 0 15px rgba(255, 0, 255, 0.8) !important;
}
[data-testid="stMetricLabel"] {
    color: #00FFFF !important;
    font-weight: bold !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.1rem !important;
    text-transform: uppercase;
}

/* Tabela de Dados (Dataframe) */
[data-testid="stDataFrame"] {
    border: 1px solid #00FFFF;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
}

</style>
""", unsafe_allow_html=True)

# Titulo principal
st.title("💻 SYS.TERMINAL // STEAM_MARKET_INTELLIGENCE")
st.markdown(">>> ACESSANDO BANCO DE DADOS GLOBAL E NACIONAL... [OK]")
st.markdown("---")

# Carregar dados
@st.cache_data
def carregar_dados():
    df_rank = pd.read_csv('data/processed/ranking_ivs.csv')
    df_indie = pd.read_csv('data/processed/indie_vs_aaa.csv')
    df_serie = pd.read_csv('data/processed/serie_historica.csv')
    df_heat = pd.read_csv('data/processed/ivs_por_genero_e_preco.csv')
    
    try:
        df_paises = pd.read_csv('data/processed/paises.csv')
    except Exception:
        df_paises = pd.DataFrame()
        
    import sqlite3
    try:
        conn = sqlite3.connect('data/steam_games.db')
        df_brasil = pd.read_sql_query("SELECT * FROM games WHERE country = 'Brazil'", conn)
        conn.close()
    except Exception:
        df_brasil = pd.DataFrame()
        
    return df_rank, df_indie, df_serie, df_heat, df_paises, df_brasil

try:
    df_rank, df_indie, df_serie, df_heat, df_paises, df_brasil = carregar_dados()
except Exception as e:
    st.error(f"ERRO DE SISTEMA: {e}")
    st.stop()


def render_chart_with_insight(fig, title, explanation, insight):
    """Funcao auxiliar para plotar o grafico na esquerda e o insight na direita."""
    st.subheader(f"► {title}")
    c_chart, c_text = st.columns([2.5, 1.2])
    
    # Aplicando fundo transparente aos graficos para combinar com o tema
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    with c_chart:
        st.plotly_chart(fig, use_container_width=True)
        
    with c_text:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">INFO_DUMP // Legenda</div>
            {explanation}
            <hr style="border-color: #333; margin: 15px 0;">
            <div class="insight-title">ANALYSIS // Insight</div>
            {insight}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

# Criando as Abas
tab1, tab2 = st.tabs(["[ 🌐 RECORTE GLOBAL ]", "[ 🇧🇷 RECORTE NACIONAL ]"])

# =============================================================================
# ABA 1: MUNDO
# =============================================================================
with tab1:
    st.header("📈 SEÇÃO 1: VISÃO DE MERCADO (INDIES VS AAA)")

    st.markdown("### // SYSTEM.METRICS // GERAIS_MERCADO")
    col1, col2, col3, col4 = st.columns(4)
    total_jogos = df_indie['total'].sum()
    preco_medio = (df_indie['preco_medio'] * df_indie['total']).sum() / total_jogos
    aprovacao_media = (df_indie['aprovacao_media'] * df_indie['total']).sum() / total_jogos

    col1.metric("TOTAL JOGOS", f"{total_jogos:,.0f}".replace(',','.'))
    col2.metric("PREÇO MÉDIO", f"US$ {preco_medio:.2f}")
    col3.metric("APROVAÇÃO", f"{aprovacao_media*100:.1f}%")
    col4.metric("DOMÍNIO INDIE", f"{(df_indie[df_indie['categoria']=='Indie']['total'].values[0] / total_jogos)*100:.1f}%")
    st.markdown("---")

    # 1. Grafico de Pizza: Distribuicao
    fig_pie = px.pie(df_indie, values='total', names='categoria', hole=0.5,
                     color='categoria', color_discrete_map={'Indie':CYBER_CYAN, 'Mid-Tier':CYBER_YELLOW, 'AAA':CYBER_MAGENTA})
    fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))

    render_chart_with_insight(
        fig_pie,
        "VOLUME DE MERCADO POR FAIXA",
        "Compara o volume total de jogos publicados na Steam divididos em 3 categorias de preço: <b>Indie</b> (até US$ 20), <b>Mid-Tier</b> (US$ 21 a US$ 39) e <b>AAA</b> (US$ 40+).",
        "Os estúdios independentes são a espinha dorsal da Steam. <b>Mais de 95% do catálogo é formado por jogos baratos.</b> Apesar dos jogos AAA fazerem mais barulho no marketing, a base numérica da plataforma depende inteiramente dos indies."
    )

    # 2. Grafico de Barras: Aprovacao vs Categoria
    fig_bar = px.bar(df_indie, x='categoria', y='aprovacao_media', 
                     text_auto='.2%', color='categoria', 
                     color_discrete_map={'Indie':CYBER_CYAN, 'Mid-Tier':CYBER_YELLOW, 'AAA':CYBER_MAGENTA})
    fig_bar.update_layout(yaxis_tickformat='.0%', yaxis_title="Taxa Média de Aprovação", xaxis_title="Categoria")
    fig_bar.update_traces(marker_line_color=CYBER_CYAN, marker_line_width=1.5, opacity=0.9)

    render_chart_with_insight(
        fig_bar,
        "SATISFAÇÃO DO CLIENTE",
        "Analisa se jogos mais caros (AAA) entregam uma taxa de satisfação maior do que jogos baratos (Indie). O eixo Y mostra a porcentagem de reviews positivos.",
        "Dinheiro não garante diversão na visão dos jogadores. Os <b>jogos Indie (75% de aprovação) superam levemente os AAA (72%)</b>. Isso indica que as expectativas dos jogadores com jogos milionários de US$ 70 são muito maiores e eles não perdoam falhas, enquanto jogos Indie possuem uma base de fãs mais fiel."
    )

    # 3. Grafico de Linhas: Serie Historica
    if not df_serie.empty and len(df_serie) > 5:
        fig_line = px.line(df_serie.sort_values('year'), x='year', y='total_games', color='genre', markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_line.update_layout(yaxis_title="Total de Lançamentos", xaxis_title="Ano de Lançamento")
        
        render_chart_with_insight(
            fig_line,
            "EVOLUÇÃO HISTÓRICA DE LANÇAMENTOS",
            "Mostra quantos jogos foram lançados ano a ano agrupados por gênero. Utiliza a data extraída diretamente das páginas (Store Scraper).",
            "Apesar da amostragem (as datas estão sendo coletadas gradualmente), é visível a explosão de jogos dos gêneros <b>Action</b> e <b>Indie</b> ao longo do tempo. O mercado cresce de maneira acentuada e a competição fica cada ano mais feroz para lançar um novo jogo."
        )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SECAO 2: CUSTO-BENEFICIO
    # -------------------------------------------------------------------------
    st.header("💎 SEÇÃO 2: ÍNDICE DE VALOR STEAM (IVS)")

    df_genero_ivs = df_heat.groupby('genre')['ivs_medio'].mean().reset_index().sort_values('ivs_medio', ascending=True)
    fig_bar_h = px.bar(df_genero_ivs, x='ivs_medio', y='genre', orientation='h', text_auto='.1f', color='ivs_medio', color_continuous_scale=['#0B0B1A', '#FF00FF'])
    fig_bar_h.update_layout(xaxis_title="Score IVS Médio", yaxis_title="Gênero")

    render_chart_with_insight(
        fig_bar_h,
        "CUSTO-BENEFÍCIO GLOBAL",
        "O IVS (Índice de Valor Steam) é uma fórmula própria que calcula: <code>(Aprovação x Engajamento) / Preço</code>. Aqui tiramos a média do IVS de cada gênero, ignorando a faixa de preço.",
        "O gênero de <b>Ação</b> e <b>Adventure</b> dominam. Eles oferecem experiências muito engajantes e normalmente possuem uma base de fãs gigantesca que impulsiona o volume de reviews. Gêneros de nicho (Sports, Strategy) ficam para trás no ranking global de custo-benefício."
    )

    heatmap_data = df_heat.pivot(index='faixa_preco', columns='genre', values='ivs_medio').fillna(0)
    ordem_preco = ['Gratuito', 'Ate R$15', 'R$15-30', 'R$30-60', 'Acima de R$60']
    heatmap_data = heatmap_data.reindex(ordem_preco)

    fig_heat = px.imshow(heatmap_data, text_auto=".1f", aspect="auto", 
                         color_continuous_scale=['#0B0B1A', '#00FFFF', '#FFFF00', '#FF00FF'],
                         labels=dict(x="Gênero", y="Faixa de Preço", color="IVS Score"))

    render_chart_with_insight(
        fig_heat,
        "HEATMAP: ONDE SEU DINHEIRO RENDE MAIS?",
        "Um mapa de calor (Heatmap) cruzando faixas de preços específicas contra os gêneros. <b>Cores mais quentes (Rosa/Amarelo)</b> indicam um valor de IVS altíssimo (um investimento excelente do seu tempo e dinheiro).",
        "Jogos <b>Gratuitos de Ação e Aventura</b> disparam no índice, pois oferecem alto engajamento a custo zero (ex: CS:GO, Apex). No segmento pago, os <b>jogos Casuais de até R$ 15</b> são as grandes 'pechinchas' absolutas, onde o jogador sente que paga muito pouco por uma diversão imensa."
    )

    st.subheader("► DISPERSÃO DO TOP 200: PREÇO VS APROVAÇÃO")
    fig_scatter = px.scatter(df_rank, x='price_usd', y='approval_rate', color='genre', size='total_reviews',
                             hover_data=['name'], opacity=0.8, size_max=40, color_discrete_sequence=px.colors.qualitative.Bold)
    fig_scatter.update_layout(xaxis_title="Preço (US$)", yaxis_title="Taxa de Aprovação", yaxis_tickformat=".0%", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    c_chart, c_text = st.columns([2.5, 1.2])
    with c_chart:
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c_text:
        st.markdown("""
        <div class="insight-box">
            <div class="insight-title">INFO_DUMP // Legenda</div>
            Cada bolha representa um jogo no **Top 200 do IVS**. 
            <ul>
                <li><b>Eixo X:</b> Preço (US$)</li>
                <li><b>Eixo Y:</b> Taxa de Aprovação</li>
                <li><b>Tamanho da Bolha:</b> Volume de Reviews</li>
            </ul>
            <hr style="border-color: #333; margin: 15px 0;">
            <div class="insight-title">ANALYSIS // Insight</div>
            Existe uma aglomeração gigantesca de bolhas no canto esquerdo superior: <b>jogos extremamente baratos (perto de US$ 0) com quase 100% de aprovação.</b><br><br>
            Isso comprova matematicamente o <i>'Padrão dos 49 Centavos'</i>: a base da Steam recompensa muito os jogos 'Meme' baratinhos, criando um viés fortíssimo de avaliação positiva.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🏆 TERMINAL // TOP 20 RANKING CUSTO-BENEFÍCIO")
    df_display = df_rank[['name', 'genre', 'price_usd', 'approval_rate', 'total_reviews', 'ivs_score']].head(20).copy()
    df_display['price_usd'] = df_display['price_usd'].apply(lambda x: f"US$ {x:.2f}")
    df_display['approval_rate'] = df_display['approval_rate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['ivs_score'] = df_display['ivs_score'].apply(lambda x: f"{x:.1f}")
    st.dataframe(df_display, use_container_width=True)
    st.markdown("---")

    # -------------------------------------------------------------------------
    # SECAO 3: ANALISE GEOGRAFICA
    # -------------------------------------------------------------------------
    if not df_paises.empty:
        st.header("🌎 SEÇÃO 3: ANÁLISE GEOGRÁFICA (WIKIDATA API)")
        st.markdown("Para contornar a limitação da API da Steam, que não fornece o País de Origem, criamos um pipeline de **Enriquecimento de Dados** conectando o Banco à API do *Wikidata* para cruzar os estúdios (Developers) com seus países Sede.")
        
        df_paises_top = df_paises.head(15).sort_values('total_jogos', ascending=True)
        fig_map = px.bar(df_paises_top, x='total_jogos', y='country', orientation='h',
                         text_auto=True, color='total_jogos', color_continuous_scale=['#0B0B1A', '#00FFFF'])
                         
        render_chart_with_insight(
            fig_map,
            "DISTRIBUIÇÃO GLOBAL DE DESENVOLVIMENTO",
            "Mostra os países com o maior volume de estúdios (que conseguimos mapear). Os Estados Unidos, Japão e Reino Unido costumam ser as maiores potências.",
            "<b>Insights de Enriquecimento:</b> Este gráfico só existe porque fizemos um JOIN entre nossa base local e a base aberta do Wikidata. O domínio dos <b>EUA</b> e <b>Japão</b> já era esperado, mas notar a presença de países como <b>França</b> (graças à Ubisoft) e <b>Coreia do Sul</b> (KRAFTON) explica como o mercado asiático está ganhando relevância em jogos de alto engajamento."
        )


# =============================================================================
# ABA 2: BRASIL
# =============================================================================
with tab2:
    if not df_brasil.empty:
        st.header("🇧🇷 SEÇÃO 4: RECORTE NACIONAL (MERCADO BRASILEIRO)")
        st.markdown("Uma análise aprofundada focada **apenas** nos estúdios localizados no Brasil. O que nossos desenvolvedores andam publicando e como estamos frente ao mercado global?")
        
        st.markdown("### // SYSTEM.METRICS // GERAIS_BRASIL")
        col1, col2, col3, col4 = st.columns(4)
        total_br = len(df_brasil)
        preco_br = df_brasil['price_usd'].mean()
        aprov_br = df_brasil['approval_rate'].mean()
        ivs_br = df_brasil['ivs'].mean()
        
        col1.metric("JOGOS BRASILEIROS", f"{total_br}")
        col2.metric("PREÇO MÉDIO", f"US$ {preco_br:.2f}")
        col3.metric("APROVAÇÃO BR", f"{aprov_br*100:.1f}%")
        col4.metric("IVS BR", f"{ivs_br:.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_br_genre = df_brasil['genre'].value_counts().reset_index()
        df_br_genre.columns = ['genre', 'total']
        fig_br_pie = px.pie(df_br_genre, values='total', names='genre', hole=0.5,
                            color='genre', color_discrete_sequence=px.colors.qualitative.Bold)
        fig_br_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
        
        render_chart_with_insight(
            fig_br_pie,
            "FOCO DO DESENVOLVIMENTO BRASILEIRO",
            "O volume de jogos criados por estúdios Brasileiros divididos por gênero principal.",
            "A indústria brasileira na Steam é essencialmente dominada pelo segmento <b>Casual</b> e <b>Indie</b> (juntos formam mais de 90% da produção). Isso ocorre por termos um ecossistema focado em equipes pequenas, estúdios nascentes e orçamentos limitados, o que torna quase impossível o desenvolvimento em massa de gêneros hiper-complexos como RPGs massivos ou AAA."
        )
        
        df_br_dev = df_brasil[df_brasil['total_reviews'] > 50].groupby('developer')['approval_rate'].mean().reset_index()
        df_br_dev = df_br_dev.sort_values('approval_rate', ascending=False).head(10)
        fig_br_bar = px.bar(df_br_dev, x='approval_rate', y='developer', orientation='h',
                            text_auto='.1%', color='approval_rate', color_continuous_scale=['#0B0B1A', '#00FFFF'])
        fig_br_bar.update_layout(xaxis_tickformat='.0%')
        
        render_chart_with_insight(
            fig_br_bar,
            "TOP DEVELOPERS DO BRASIL EM QUALIDADE",
            "Ranqueamento dos estúdios brasileiros com base na aprovação média recebida pelos jogadores globais. Considera apenas estúdios cujo portfólio passou de um volume básico de 50 análises.",
            "<b>Insight Forte de Mercado:</b> O Brasil produz jogos de <b>altíssima qualidade</b> para seu nicho! Enquanto a média de aprovação global dos jogos da Steam é de 75%, os estúdios brasileiros atingem impressionantes <b>82,5%</b> de média geral, com o Top 10 batendo taxas perfeitas perto de 99% a 100%. Quando o Brasil consegue publicar, ele agrada demais o público."
        )
        
        df_brasil['categoria'] = pd.cut(df_brasil['price_usd'], bins=[-1, 20.0, 39.99, float('inf')], labels=['Indie', 'Mid-Tier', 'AAA'])
        df_brasil['faixa_preco'] = pd.cut(df_brasil['price_usd'], bins=[-1, 0.001, 2.80, 5.70, 11.50, float('inf')], 
                                          labels=['Gratuito', 'Ate R$15', 'R$15-30', 'R$30-60', 'Acima de R$60'])
        df_brasil['year'] = pd.to_datetime(df_brasil['release_date'], errors='coerce').dt.year

        df_br_cat = df_brasil.groupby('categoria', observed=False)['approval_rate'].mean().reset_index().dropna()
        if not df_br_cat.empty:
            fig_br_cat = px.bar(df_br_cat, x='categoria', y='approval_rate', text_auto='.2%', 
                                color='categoria', color_discrete_map={'Indie':CYBER_CYAN, 'Mid-Tier':CYBER_YELLOW, 'AAA':CYBER_MAGENTA})
            fig_br_cat.update_layout(yaxis_tickformat='.0%', yaxis_title="Aprovação Média", xaxis_title="Categoria")
            fig_br_cat.update_traces(marker_line_color=CYBER_CYAN, marker_line_width=1.5, opacity=0.9)
            render_chart_with_insight(
                fig_br_cat,
                "SATISFAÇÃO NO BRASIL (INDIE X MID-TIER X AAA)",
                "Mede o quão satisfeitos os jogadores estão com os jogos brasileiros dependendo do nível de investimento do jogo.",
                "Semelhante ao mercado global, os jogos Indie brasileiros dominam a satisfação. Curiosamente, quase não temos representatividade na faixa AAA, reforçando que a força nacional está em jogos criativos e baratos."
            )

        df_br_serie = df_brasil.dropna(subset=['year']).groupby(['year', 'genre'], observed=False).size().reset_index(name='total')
        if not df_br_serie.empty and len(df_br_serie) > 3:
            fig_br_serie = px.line(df_br_serie.sort_values('year'), x='year', y='total', color='genre', markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_br_serie.update_layout(yaxis_title="Total de Lançamentos", xaxis_title="Ano")
            render_chart_with_insight(
                fig_br_serie,
                "EVOLUÇÃO HISTÓRICA NACIONAL",
                "Mapeia o ritmo de publicação de novos jogos pelos estúdios brasileiros na Steam ao longo dos anos.",
                "É perceptível a curva de aceleração de lançamentos no Brasil, especialmente no gênero <b>Casual</b> e <b>Indie</b>, acompanhando a democratização de engines gratuitas como Unity e Godot no mercado nacional."
            )

        df_br_heat = df_brasil.groupby(['faixa_preco', 'genre'], observed=False)['ivs'].mean().reset_index()
        if not df_br_heat.empty:
            heatmap_br_data = df_br_heat.pivot(index='faixa_preco', columns='genre', values='ivs').fillna(0)
            heatmap_br_data = heatmap_br_data.reindex(['Gratuito', 'Ate R$15', 'R$15-30', 'R$30-60', 'Acima de R$60'])
            fig_br_heat = px.imshow(heatmap_br_data, text_auto=".1f", aspect="auto", 
                                    color_continuous_scale=['#0B0B1A', '#00FFFF', '#FFFF00', '#FF00FF'],
                                    labels=dict(x="Gênero", y="Faixa de Preço", color="IVS Score"))
            render_chart_with_insight(
                fig_br_heat,
                "HEATMAP: ONDE O DINHEIRO RENDE MAIS NO BRASIL?",
                "Cruzamento das faixas de preço brasileiras com os gêneros focando no Custo-Benefício.",
                "Assim como no cenário Global, os jogos Gratuitos e Casuais de até R$ 15 brilham no Brasil. O desenvolvedor nacional tem uma forte veia para jogos de baixo custo, o que atrai um público fiel que valoriza muito essas experiências."
            )

        st.subheader("► DISPERSÃO NACIONAL: PREÇO VS APROVAÇÃO")
        df_br_scatter = df_brasil[df_brasil['ivs'] > 0]
        if not df_br_scatter.empty:
            fig_br_scatter = px.scatter(df_br_scatter, x='price_usd', y='approval_rate', color='genre', size='total_reviews',
                                        hover_data=['name'], opacity=0.8, size_max=40, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_br_scatter.update_layout(xaxis_title="Preço (US$)", yaxis_title="Taxa de Aprovação", yaxis_tickformat=".0%", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            c_chart, c_text = st.columns([2.5, 1.2])
            with c_chart:
                st.plotly_chart(fig_br_scatter, use_container_width=True)
            with c_text:
                st.markdown("""
                <div class="insight-box">
                    <div class="insight-title">INFO_DUMP // Legenda</div>
                    Mostra todos os jogos brasileiros mapeados. Bolhas maiores significam mais jogadores avaliando.<br>Eixo X = Preço, Eixo Y = Aprovação.
                    <hr style="border-color: #333; margin: 15px 0;">
                    <div class="insight-title">ANALYSIS // Insight</div>
                    Podemos ver claramente o aglomerado no canto superior esquerdo. <b>A esmagadora maioria dos sucessos absolutos do Brasil (com mais de 90% de aprovação e muitas reviews) custam menos de 10 dólares.</b><br><br>
                    Isso confirma que o estúdio brasileiro entende muito bem as dores do seu público, cobrando um preço justo e colhendo altíssima satisfação.
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("---")

        # ---------------------------------------------------------------------
        # SECAO 5: CONCLUSÃO COMPARATIVA
        # ---------------------------------------------------------------------
        st.header("🎯 SEÇÃO 5: SÍNTESE ESTRATÉGICA (GLOBAL VS BRASIL)")
        st.markdown("Comparando os cenários lado a lado, geramos inteligência de mercado cruzada para responder a uma pergunta central: *Como a indústria de jogos Brasileira se posiciona frente ao resto do mundo?*")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""
            <div class="insight-box" style="border-left: 5px solid #FFFF00;">
                <div class="insight-title">1. DAVI VS GOLIAS</div>
                O Brasil representa uma fração minúscula do volume de mercado (pouco mais de 400 jogos contra os 84.000 mapeados globalmente). No entanto, a <b>Aprovação Média Brasileira é de 82,5% (contra 75% Global)</b>. 
                <br><br>
                <i>O que isso significa?</i> O desenvolvedor brasileiro foca no "tiro certo". Não produzimos em massa, mas nossos estúdios entregam experiências lapidadas que raramente decepcionam a comunidade de nicho que compra os jogos.
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="insight-box" style="border-left: 5px solid #FF00FF;">
                <div class="insight-title">2. A AUSÊNCIA DO AAA</div>
                No cenário global, jogos de 70 dólares (AAA) movimentam os portais de notícias e possuem sua fatia estabelecida. No Brasil, essa categoria é praticamente inexistente. A nossa indústria é <b>95% composta por Indie e Casuais</b>.
                <br><br>
                <i>O que isso significa?</i> O Brasil joga o jogo que consegue vencer. Com financiamento reduzido, a força criativa do país canalizou seu talento para fazer jogos criativos, baratos e eficientes, driblando a necessidade de orçamentos milionários.
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="insight-box" style="border-left: 5px solid #00FFFF;">
                <div class="insight-title">3. O VIÉS DO PREÇO</div>
                O nosso principal insight metodológico ("O Padrão dos 49 Centavos") se confirmou perfeitamente nos dois cenários. Tanto no Mundo quanto no Brasil, a aglomeração de altíssima aprovação ocorre nos jogos muito baratos (até R$ 15).
                <br><br>
                <i>O que isso significa?</i> O comportamento do consumidor Steam não muda pela cultura do país desenvolvedor. O jogador julga o "Custo-Benefício" de forma idêntica globalmente. Oferecer um jogo decente a preço de um café expresso sempre vai estourar as notas da comunidade.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background-color: rgba(255, 0, 255, 0.15); border: 2px solid #FF00FF; border-left: 10px solid #FF00FF; padding: 30px; margin-top: 30px; box-shadow: 0 0 20px rgba(255, 0, 255, 0.4);">
            <h2 style="color: #FF00FF; font-family: 'Orbitron', sans-serif; margin-top: 0; margin-bottom: 15px; text-shadow: 0 0 10px #FF00FF;">► SYS_MESSAGE // CONCLUSÃO DO PORTFÓLIO</h2>
            <p style="font-size: 24px; font-family: 'Rajdhani', sans-serif; color: #FFFFFF; font-weight: bold; line-height: 1.5; letter-spacing: 1px;">
                A indústria brasileira não tenta competir com a americana/europeia nos grandes blockbusters. Nós somos uma verdadeira fábrica de <b>Indie Games</b> que extrai um Custo-Benefício avassalador:<br><br>
                <span style="color: #00FFFF; text-shadow: 0 0 8px #00FFFF; font-size: 28px;">Cobrando pouco e entregando taxas de aprovação que os gigantes do mercado sonham em ter!</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
