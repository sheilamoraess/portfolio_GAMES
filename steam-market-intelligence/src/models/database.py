import sqlite3
import pandas as pd
from typing import List
from models.game import Game


class Database:
    """
    Gerencia a conexao e o schema do banco SQLite.
    Toda persistencia de dados passa por esta classe.
    """

    def __init__(self, db_path: str = 'data/steam_games.db'):
        self.db_path = db_path
        self._init_schema()

    # ------------------------------------------------------------------
    # Conexao
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self):
        """Cria as tabelas e indices se ainda nao existirem."""
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    app_id           INTEGER PRIMARY KEY,
                    name             TEXT    NOT NULL,
                    developer        TEXT,
                    publisher        TEXT,
                    genre            TEXT,
                    release_date     TEXT,
                    price_usd        REAL,
                    positive_reviews INTEGER,
                    negative_reviews INTEGER,
                    total_reviews    INTEGER,
                    approval_rate    REAL,
                    avg_playtime_h   REAL,
                    peak_ccu         INTEGER,
                    owners_estimate  TEXT,
                    ivs              REAL,
                    coletado_em      TEXT DEFAULT (datetime('now'))
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS genre_history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    genre       TEXT,
                    year        INTEGER,
                    total_games INTEGER,
                    avg_price   REAL,
                    avg_reviews REAL,
                    avg_ivs     REAL
                )
            ''')

            conn.execute('CREATE INDEX IF NOT EXISTS idx_genre   ON games(genre)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_release ON games(release_date)')

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def inserir_games(self, games: List[Game]):
        """Insere ou atualiza uma lista de objetos Game no banco."""
        with self._connect() as conn:
            for game in games:
                conn.execute('''
                    INSERT OR REPLACE INTO games
                    VALUES (
                        :app_id, :name, :developer, :publisher, :genre,
                        :release_date, :price_usd, :positive_reviews,
                        :negative_reviews, :total_reviews, :approval_rate,
                        :avg_playtime_h, :peak_ccu, :owners_estimate,
                        :ivs, datetime('now')
                    )
                ''', game.to_dict())

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def buscar_todos(self) -> pd.DataFrame:
        """Retorna todos os jogos como DataFrame."""
        with self._connect() as conn:
            return pd.read_sql('SELECT * FROM games', conn)

    def buscar_por_genero(self, genero: str) -> pd.DataFrame:
        """Retorna jogos de um genero especifico."""
        with self._connect() as conn:
            return pd.read_sql(
                'SELECT * FROM games WHERE genre = ?', conn, params=[genero]
            )

    def total_jogos(self) -> int:
        """Retorna o total de jogos cadastrados no banco."""
        with self._connect() as conn:
            resultado = conn.execute('SELECT COUNT(*) FROM games').fetchone()
            return resultado[0]
