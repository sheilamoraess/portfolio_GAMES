import sys
import os

# Garante que o Python encontra os modulos dentro de src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import Database
from collectors.steamspy_collector import SteamSpyCollector
from collectors.steam_scraper import SteamStoreScraper
from exporters.exporter import Exporter

# ------------------------------------------------------------------
# Configuracao
# ------------------------------------------------------------------

GENEROS = [
    'Action',
    'Adventure',
    'RPG',
    'Strategy',
    'Simulation',
    'Sports',
    'Indie',
    'Casual',
]

DB_PATH      = 'data/steam_games.db'
LIMIT_SCRAPE = 300  # quantos jogos enriquecer via scraping


# ------------------------------------------------------------------
# Pipeline principal
# ------------------------------------------------------------------

if __name__ == '__main__':
    db       = Database(db_path=DB_PATH)
    exporter = Exporter(db)

    banco_vazio = db.total_jogos() == 0

    if banco_vazio:
        # --- PRIMEIRA EXECUCAO ---
        # Coleta e salva os dados. Nao repete nas proximas vezes.

        print('Banco vazio detectado. Iniciando coleta inicial...')

        print('\n=== ETAPA 1: Coleta SteamSpy ===')
        collector = SteamSpyCollector(db)
        collector.executar_coleta_completa(GENEROS)

        print('\n=== ETAPA 2: Enriquecimento Steam Store ===')
        scraper = SteamStoreScraper(db)
        scraper.enriquecer_banco(limit=LIMIT_SCRAPE)

        print('\nColeta inicial concluida. Banco salvo em:', DB_PATH)

    else:
        # --- EXECUCOES SEGUINTES ---
        # Banco ja populado. Apenas processa e exporta.
        print(f'Banco encontrado com {db.total_jogos()} jogos. Pulando coleta.')

    # Etapa 3 — Processamento e exportacao (sempre executa)
    print('\n=== Processamento e Exportacao ===')
    exporter.relatorio_banco()
    exporter.exportar_todos()

    print('\nPipeline concluido. CSVs prontos em data/processed/')
