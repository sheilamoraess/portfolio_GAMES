import sqlite3
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

from models.database import Database


class SteamStoreScraper:
    """
    Enriquece os jogos do banco com dados da Steam Store
    que a SteamSpy nao fornece: tags dos usuarios,
    numero de conquistas e descricao curta do jogo.
    """

    BASE_URL      = 'https://store.steampowered.com/app/'
    DELAY_SECONDS = 2.0  # scraping exige delay maior que a API

    def __init__(self, database: Database):
        self.db      = database
        self.session = requests.Session()

        # Cookie para pular o aviso de verificacao de idade
        self.session.cookies.set('birthtime',      '631152001', domain='store.steampowered.com')
        self.session.cookies.set('lastagecheckage', '1-0-2000', domain='store.steampowered.com')
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; portfolio-project/1.0)'
        })

    # ------------------------------------------------------------------
    # Scraping de uma pagina
    # ------------------------------------------------------------------

    def scrape_game(self, app_id: int) -> Optional[dict]:
        """
        Faz o scraping da pagina de um jogo e extrai:
        - tags populares definidas pelos usuarios
        - numero de conquistas
        - descricao curta
        Retorna None em caso de falha.
        """
        url = f'{self.BASE_URL}{app_id}/'
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Tags populares (maximo 5)
            tags = [
                tag.text.strip()
                for tag in soup.select('a.app_tag')
            ]

            # Numero de conquistas
            conquistas_el = soup.select_one('.block_title.online_achievement_block')
            conquistas    = conquistas_el.text.strip() if conquistas_el else '0'

            # Descricao curta (max 300 caracteres)
            desc_el  = soup.select_one('.game_description_snippet')
            descricao = desc_el.text.strip()[:300] if desc_el else ''

            # Data de lancamento
            data_el    = soup.select_one('.date')
            release_date = data_el.text.strip() if data_el else None

            return {
                'app_id':       app_id,
                'tags':         ', '.join(tags[:5]),
                'conquistas':   conquistas,
                'descricao':    descricao,
                'release_date': release_date,
            }

        except Exception as e:
            print(f'  [AVISO] Erro no scraping do app {app_id}: {e}')
            return None

    # ------------------------------------------------------------------
    # Enriquecimento em lote
    # ------------------------------------------------------------------

    def _garantir_colunas(self, conn: sqlite3.Connection):
        """Adiciona as colunas de enriquecimento se ainda nao existirem."""
        for coluna in ['tags TEXT', 'conquistas TEXT', 'descricao TEXT']:
            try:
                conn.execute(f'ALTER TABLE games ADD COLUMN {coluna}')
            except Exception:
                pass  # coluna ja existe, ignorar

    def enriquecer_banco(self, limit: int = 500):
        """
        Busca jogos sem tags no banco e faz o scraping de cada um.
        Atualiza o registro com os dados coletados.
        """
        with sqlite3.connect(self.db.db_path) as conn:
            self._garantir_colunas(conn)
            ids = conn.execute(
                'SELECT app_id FROM games WHERE tags IS NULL LIMIT ?', [limit]
            ).fetchall()

        total = len(ids)
        print(f'Iniciando enriquecimento de {total} jogos...')

        for i, (app_id,) in enumerate(ids, start=1):
            print(f'  [{i}/{total}] app_id={app_id}')
            dados = self.scrape_game(app_id)

            if dados:
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.execute('''
                        UPDATE games
                        SET tags = ?, conquistas = ?, descricao = ?, release_date = ?
                        WHERE app_id = ?
                    ''', (dados['tags'], dados['conquistas'],
                          dados['descricao'], dados['release_date'], app_id))

            time.sleep(self.DELAY_SECONDS)

        print('Enriquecimento concluido.')
