import pandas as pd
from models.database import Database


class MarketProcessor:
    """
    Analisa a evolucao historica do mercado de games na Steam.
    Trabalha com os dados do banco e produz DataFrames prontos
    para exportacao ao Power BI.
    """

    def __init__(self, database: Database):
        self.db = database

    # ------------------------------------------------------------------
    # Analise temporal
    # ------------------------------------------------------------------

    def _carregar_com_ano(self) -> pd.DataFrame:
        """
        Carrega todos os jogos e extrai o ano de lancamento.
        Filtra apenas jogos com data valida entre 2010 e 2024.
        """
        df = self.db.buscar_todos()
        df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        df = df[df['year'].between(2010, 2024)]
        return df

    def serie_historica_por_genero(self) -> pd.DataFrame:
        """
        Agrega lancamentos por genero e ano.
        Base para o grafico de area empilhada no Power BI.
        """
        df = self._carregar_com_ano()

        return (
            df.groupby(['year', 'genre'])
            .agg(
                total_games = ('app_id',      'count'),
                avg_price   = ('price_usd',   'mean'),
                avg_reviews = ('total_reviews','mean'),
                avg_ivs     = ('ivs',          'mean'),
            )
            .reset_index()
            .round(2)
        )

    def crescimento_por_genero(self) -> pd.DataFrame:
        """
        Calcula taxa de crescimento ano a ano (YoY) por genero.
        Identifica quais generos estao em ascensao ou declinio.
        """
        serie = self.serie_historica_por_genero()
        serie = serie.sort_values(['genre', 'year'])
        serie['crescimento_yoy'] = (
            serie.groupby('genre')['total_games']
            .pct_change() * 100
        )
        return serie.round(2)

    # ------------------------------------------------------------------
    # Comparativo de categorias
    # ------------------------------------------------------------------

    def dominio_indie_vs_aaa(self) -> pd.DataFrame:
        """
        Classifica jogos em Indie, Mid-Tier ou AAA pelo preco
        e compara volume, aprovacao e IVS medio entre os grupos.
        """
        df = self.db.buscar_todos()
        df['categoria'] = df['price_usd'].apply(
            lambda p: 'AAA' if p >= 40 else ('Indie' if p <= 20 else 'Mid-Tier')
        )

        return (
            df.groupby('categoria')
            .agg(
                total           = ('app_id',        'count'),
                preco_medio     = ('price_usd',      'mean'),
                aprovacao_media = ('approval_rate',  'mean'),
                ivs_medio       = ('ivs',            'mean'),
                playtime_medio_h= ('avg_playtime_h', 'mean'),
            )
            .reset_index()
            .round(2)
        )

    # ------------------------------------------------------------------
    # Exportacao
    # ------------------------------------------------------------------

    def exportar_para_powerbi(self, output_path: str = 'data/processed/'):
        """Salva os CSVs de mercado prontos para o Power BI."""
        serie = self.crescimento_por_genero()
        serie.to_csv(f'{output_path}serie_historica.csv', index=False)

        indie = self.dominio_indie_vs_aaa()
        indie.to_csv(f'{output_path}indie_vs_aaa.csv', index=False)

        print('Exportacao para Power BI concluida.')
        print(f'  -> {output_path}serie_historica.csv')
        print(f'  -> {output_path}indie_vs_aaa.csv')
