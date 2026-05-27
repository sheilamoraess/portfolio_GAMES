import pandas as pd
from models.database import Database


class ValueProcessor:
    """
    Calcula e ranqueia jogos pelo Indice de Valor Steam (IVS).
    Produz DataFrames prontos para exportacao ao Tableau.
    """

    # Minimo de reviews para entrar no ranking
    # (playtime nao filtrado: API publica nao retorna esse dado)
    MIN_REVIEWS = 500

    def __init__(self, database: Database):
        self.db = database

    # ------------------------------------------------------------------
    # Filtragem e normalizacao
    # ------------------------------------------------------------------

    def _filtrar_e_normalizar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica filtros de qualidade minima e normaliza o IVS
        para uma escala de 0 a 100, facilitando a leitura no dashboard.
        """
        df = df[
            (df['total_reviews'] >= self.MIN_REVIEWS) &
            (df['ivs']           >  0)
        ].copy()

        ivs_min = df['ivs'].min()
        ivs_max = df['ivs'].max()
        df['ivs_score'] = (
            (df['ivs'] - ivs_min) / (ivs_max - ivs_min) * 100
        ).round(1)

        df['faixa_preco'] = pd.cut(
            df['price_usd'],
            bins=[-1, 0, 15, 30, 60, 999],
            labels=['Gratuito', 'Ate R$15', 'R$15-30', 'R$30-60', 'Acima de R$60']
        )

        return df

    # ------------------------------------------------------------------
    # Rankings
    # ------------------------------------------------------------------

    def ranking_custo_beneficio(self, top_n: int = 200) -> pd.DataFrame:
        """
        Retorna os top N jogos com melhor custo-beneficio pelo IVS Score.
        """
        df = self.db.buscar_todos()
        df = self._filtrar_e_normalizar(df)

        colunas = [
            'app_id', 'name', 'genre', 'developer',
            'price_usd', 'faixa_preco', 'approval_rate',
            'avg_playtime_h', 'total_reviews', 'ivs', 'ivs_score',
        ]

        # Inclui coluna tags somente se existir (adicionada pelo scraper)
        if 'tags' in df.columns:
            colunas.append('tags')

        return (
            df[colunas]
            .sort_values('ivs_score', ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )

    def melhor_genero_por_faixa_de_preco(self) -> pd.DataFrame:
        """
        Qual genero entrega mais valor em cada faixa de preco?
        Base para o heatmap no Tableau.
        """
        df = self._filtrar_e_normalizar(self.db.buscar_todos())

        return (
            df.groupby(['faixa_preco', 'genre'], observed=False)
            .agg(
                ivs_medio   = ('ivs_score', 'mean'),
                total_jogos = ('app_id',    'count'),
            )
            .reset_index()
            .sort_values(['faixa_preco', 'ivs_medio'], ascending=[True, False])
            .round(2)
        )

    # ------------------------------------------------------------------
    # Exportacao
    # ------------------------------------------------------------------

    def exportar_para_tableau(self, output_path: str = 'data/processed/'):
        """Salva os CSVs de custo-beneficio prontos para o Tableau."""
        ranking    = self.ranking_custo_beneficio()
        por_genero = self.melhor_genero_por_faixa_de_preco()

        ranking.to_csv(f'{output_path}ranking_ivs.csv', index=False)
        por_genero.to_csv(f'{output_path}ivs_por_genero_e_preco.csv', index=False)

        print('Exportacao para Tableau concluida.')
        print(f'  -> {output_path}ranking_ivs.csv')
        print(f'  -> {output_path}ivs_por_genero_e_preco.csv')
