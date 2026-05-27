from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Game:
    """
    Representa um jogo da Steam.
    Os campos calculados (total_reviews, approval_rate, ivs)
    sao preenchidos automaticamente no __post_init__.
    """

    app_id: int
    name: str
    developer: str
    publisher: str
    genre: str
    release_date: Optional[date]
    price_usd: float
    positive_reviews: int
    negative_reviews: int
    owners_estimate: str          # ex: "1,000,000 .. 2,000,000"
    average_playtime_forever: int  # em minutos
    peak_ccu: int                 # pico de jogadores simultaneos

    # Calculados automaticamente — nao passar na construcao
    total_reviews: int   = field(init=False)
    approval_rate: float = field(init=False)
    ivs: float           = field(init=False)  # Indice de Valor Steam

    def __post_init__(self):
        self.total_reviews = self.positive_reviews + self.negative_reviews
        self.approval_rate = (
            self.positive_reviews / self.total_reviews
            if self.total_reviews > 0 else 0.0
        )
        self.ivs = self._calcular_ivs()

    # ------------------------------------------------------------------
    # Logica de negocio
    # ------------------------------------------------------------------

    def _calcular_ivs(self) -> float:
        """
        Indice de Valor Steam (IVS).

        Formula primaria  : (aprovacao * horas_de_jogo) / preco_ajustado
        Formula alternativa: (aprovacao * log10(reviews + 1)) / preco_ajustado
            - Usada quando playtime nao esta disponivel (limitacao da API publica)
            - log10 normaliza reviews grandes sem distorcer o ranking

        Jogos gratuitos recebem penalidade leve (0.8) para nao dominar
        o ranking apenas por serem gratuitos.
        """
        import math

        if self.price_usd <= 0:
            preco_ajustado = 1.0
            penalidade     = 0.8
        else:
            preco_ajustado = self.price_usd
            penalidade     = 1.0

        horas = self.average_playtime_forever / 60

        if horas > 0:
            # Dado real de playtime disponivel
            engajamento = horas
        else:
            # Proxy: log10 do total de reviews
            engajamento = math.log10(self.total_reviews + 1)

        ivs = (self.approval_rate * engajamento / preco_ajustado) * penalidade
        return round(ivs, 4)

    # ------------------------------------------------------------------
    # Serializacao
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Converte o objeto para dicionario compativel com o banco."""
        return {
            'app_id':           self.app_id,
            'name':             self.name,
            'developer':        self.developer,
            'publisher':        self.publisher,
            'genre':            self.genre,
            'release_date':     str(self.release_date) if self.release_date else None,
            'price_usd':        self.price_usd,
            'positive_reviews': self.positive_reviews,
            'negative_reviews': self.negative_reviews,
            'total_reviews':    self.total_reviews,
            'approval_rate':    self.approval_rate,
            'avg_playtime_h':   round(self.average_playtime_forever / 60, 1),
            'peak_ccu':         self.peak_ccu,
            'owners_estimate':  self.owners_estimate,
            'ivs':              self.ivs,
        }
