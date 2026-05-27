import requests
import time
from datetime import date, datetime
from typing import List, Optional

from models.game import Game
from models.database import Database


class SteamSpyCollector:
    """
    Coleta dados de jogos via API publica do SteamSpy.
    Sem autenticacao. Respeita o rate limit com delay entre requisicoes.
    """

    BASE_URL      = 'https://steamspy.com/api.php'
    DELAY_SECONDS = 1.5  # intervalo entre chamadas para nao ser bloqueado

    def __init__(self, database: Database):
        self.db      = database
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'steam-portfolio-project/1.0'})

    # ------------------------------------------------------------------
    # Comunicacao com a API
    # ------------------------------------------------------------------

    def _get(self, params: dict) -> dict:
        """Faz a requisicao GET e retorna o JSON."""
        response = self.session.get(self.BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Converte a string de data da API para objeto date."""
        for fmt in ['%b %d, %Y', '%b %Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except (ValueError, TypeError):
                continue
        return None

    def _parse_game(self, data: dict, genero: str = 'Unknown') -> Optional[Game]:
        """
        Converte um item do JSON da API em objeto Game.
        O parametro genero vem da chamada de coleta, pois o endpoint
        de genero da SteamSpy nao retorna esse campo em cada jogo.
        Retorna None se os dados forem invalidos ou incompletos.
        """
        try:
            return Game(
                app_id                   = int(data['appid']),
                name                     = data.get('name', 'Unknown'),
                developer                = data.get('developer', 'Unknown'),
                publisher                = data.get('publisher', 'Unknown'),
                genre                    = genero,
                release_date             = self._parse_date(data.get('release_date', '')),
                price_usd                = int(data.get('price', 0)) / 100,
                positive_reviews         = int(data.get('positive', 0)),
                negative_reviews         = int(data.get('negative', 0)),
                owners_estimate          = data.get('owners', '0 .. 0'),
                average_playtime_forever = int(data.get('average_forever', 0)),
                peak_ccu                 = int(data.get('peak_ccu', 0)),
            )
        except Exception as e:
            print(f'  [AVISO] Erro ao parsear "{data.get("name")}": {e}')
            return None

    # ------------------------------------------------------------------
    # Coleta
    # ------------------------------------------------------------------

    def coletar_por_genero(self, genero: str) -> List[Game]:
        """
        Coleta todos os jogos de um genero via SteamSpy.
        A API retorna todos os jogos do genero em UMA unica chamada,
        entao o delay fica apenas em executar_coleta_completa (entre generos).
        """
        print(f'Coletando genero: {genero}...')
        data  = self._get({'request': 'genre', 'genre': genero})
        games = []

        for item in data.values():
            game = self._parse_game(item, genero=genero)
            if game:
                games.append(game)

        print(f'  {len(games)} jogos coletados.')
        return games

    def coletar_top_100(self) -> List[Game]:
        """Coleta os 100 jogos mais jogados das ultimas duas semanas."""
        print('Coletando top 100...')
        data = self._get({'request': 'top100in2weeks'})
        games = [
            game for game in
            (self._parse_game(item, genero='Top100') for item in data.values())
            if game is not None
        ]
        print(f'  {len(games)} jogos coletados.')
        return games

    def executar_coleta_completa(self, generos: List[str]):
        """
        Pipeline completo de coleta:
        1. Coleta jogos de cada genero
        2. Persiste tudo no banco de uma vez
        """
        todos = []

        for genero in generos:
            games = self.coletar_por_genero(genero)
            todos.extend(games)
            time.sleep(2)  # pausa extra entre generos

        self.db.inserir_games(todos)
        print(f'\nTotal inserido no banco: {len(todos)} jogos.')
