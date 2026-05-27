import os
import pandas as pd
from models.database import Database
from processors.market_processor import MarketProcessor
from processors.value_processor import ValueProcessor


class Exporter:
    """
    Centraliza a exportacao de todos os CSVs do projeto.
    Garante que a pasta de saida existe antes de salvar.
    """

    OUTPUT_PATH = 'data/processed/'

    def __init__(self, database: Database):
        self.db             = database
        self.market         = MarketProcessor(database)
        self.value          = ValueProcessor(database)
        os.makedirs(self.OUTPUT_PATH, exist_ok=True)

    # ------------------------------------------------------------------
    # Exportacoes individuais
    # ------------------------------------------------------------------

    def exportar_mercado(self):
        """Exporta os CSVs da Secao 1 (Power BI)."""
        print('\n--- Exportando dados de mercado ---')
        self.market.exportar_para_powerbi(self.OUTPUT_PATH)

    def exportar_valor(self):
        """Exporta os CSVs da Secao 2 (Tableau)."""
        print('\n--- Exportando dados de custo-beneficio ---')
        self.value.exportar_para_tableau(self.OUTPUT_PATH)

    def exportar_todos(self):
        """Exporta todos os CSVs de uma vez."""
        self.exportar_mercado()
        self.exportar_valor()
        print(f'\nTodos os arquivos salvos em: {self.OUTPUT_PATH}')

    # ------------------------------------------------------------------
    # Relatorio de status
    # ------------------------------------------------------------------

    def relatorio_banco(self):
        """Exibe um resumo rapido do que esta no banco."""
        df = self.db.buscar_todos()
        if df.empty:
            print('Banco vazio.')
            return

        print('\n=== Resumo do banco ===')
        print(f'  Total de jogos  : {len(df)}')
        print(f'  Generos unicos  : {df["genre"].nunique()}')
        print(f'  Preco medio     : US$ {df["price_usd"].mean():.2f}')
        print(f'  Aprovacao media : {df["approval_rate"].mean():.1%}')
        print(f'  IVS medio       : {df["ivs"].mean():.4f}')
        print(f'  Ano mais antigo : {pd.to_datetime(df["release_date"], errors="coerce").dt.year.min():.0f}')
        print(f'  Ano mais recente: {pd.to_datetime(df["release_date"], errors="coerce").dt.year.max():.0f}')
