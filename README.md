# O Algoritmo do Sucesso na Steam
Investigação do mercado de desenvolvimento de jogos digitais e cálculo de Custo-Benefício usando Python, SQLite e Streamlit.

## Contexto
Milhares de jogos são lançados anualmente na Steam, mas apenas uma fração atinge aclamação e engajamento da comunidade. Este projeto analisa metadados de dezenas de milhares de jogos para entender o que diferencia um grande sucesso comercial de um fracasso — e responder matematicamente se existe um "padrão de preço" no mercado global e brasileiro.

## Stack
Python · Pandas · SQLite · Streamlit · Plotly · API Steam · API Wikidata

## Fonte de Dados
[SteamSpy & Steam Store API] — catálogo completo da plataforma contendo preço, engajamento (reviews), desenvolvedora, gênero, data de lançamento e taxa de aprovação.
[Wikidata SPARQL] — metadados de estúdios e cruzamento de localizações (País de Origem).

## Metodologia
1. **Coleta de Massa** — raspagem automatizada das APIs do SteamSpy e da loja oficial usando Orientação a Objetos.
2. **Modelagem de Dados** — criação de banco SQLite para persistência histórica (`steam_games.db`).
3. **Data Enrichment** — cruzamento do catálogo de estúdios da Steam com o banco semântico do Wikidata via linguagem SPARQL para mapear o País de Origem de cada jogo.
4. **Criação de Métrica (IVS)** — desenvolvimento de fórmula própria de "Índice de Valor Steam" ponderando `(Aprovação x Engajamento) / Preço`.
5. **Dashboard Cyberpunk** — aplicação web interativa construída com Streamlit e Plotly no formato dark-neon, contendo análises profundas divididas em duas abas: Global e Nacional.

## Principais Insights Globais
1. **O Padrão dos 49 Centavos** — foi provado matematicamente que existe um viés massivo de aprovação em jogos extremamente baratos (perto de US$ 0), recompensando desenvolvedores focados em volume (jogos memes e casuais).
2. **O Domínio Indie** — mais de 95% do catálogo total da Steam é formado por jogos na faixa "Indie" (até US$ 20), formando a base de publicação da plataforma.
3. **O Dinheiro Não Compra Satisfação** — títulos milionários AAA (acima de US$ 40) amargam uma média de aprovação menor (72%) do que títulos Indie (75%), evidenciando a altíssima e implacável exigência técnica por parte dos consumidores de grandes lançamentos.
4. **O Gênero Mais Engajante** — o cruzamento de Custo-Benefício mostra que "Casual" e "Ação" focados no mercado gratuito ou de até US$ 15 são as categorias de ouro para agradar o público e maximizar engajamento.

## Recorte Nacional (O Mercado Brasileiro)
Seção dedicada exclusivamente aos estúdios do Brasil, com análise de qualidade, volume e direcionamento de mercado:
- **Davi vs Golias (Qualidade > Volume)** — o Brasil tem um volume muito inferior às potências mundiais, mas apresenta uma taxa de aprovação estelar de **82,5%** (contra 75% Global).
- **A Ausência do AAA** — 95% da produção nacional também se concentra em indies e casuais. O Brasil joga o jogo que consegue vencer, contornando a falta de orçamentos milionários e entregando alta qualidade.
- **O Viés do Preço é Universal** — as mesmas regras de dispersão de preço aplicadas ao mercado europeu/americano afetam a mente do consumidor que julga os jogos brasileiros.

## Como Rodar Localmente
```bash
# 1. Clonar o repositório
git clone https://github.com/sheilamoraess/portfolio_GAMES.git
cd portfolio_GAMES

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Processar os dados (execute apenas uma vez para montar o banco de dados)
python main.py      # extrai as informações da Steam e processa o IVS
python enrich.py    # conecta no Wikidata e enriquece a análise de países

# 4. Iniciar o dashboard
python -m streamlit run dashboard.py
```
O app abre em `http://localhost:8501`.
