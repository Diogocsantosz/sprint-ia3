"""Schema Pydantic v2 do domínio EV — saída estruturada das consultas de recarga.

Quando o usuário pergunta status de estação, potência ou faturamento, a chain
estruturada devolve um ConsultaRecarga validado em vez de texto livre.
"""

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

EstadoCarregador = Literal["disponivel", "ocupado", "reservado", "offline", "manutencao"]


class ConsultaRecarga(BaseModel):
    """Resposta estruturada de uma consulta de recarga/estação."""

    estacao_id: str = Field(description="Identificador da estação, formato EST-XX")
    estado_carregador: EstadoCarregador
    potencia_kw: float = Field(gt=0, le=350, description="Potência do carregador em kW")
    energia_kwh: Optional[float] = Field(default=None, ge=0)
    custo_estimado_brl: Optional[float] = Field(default=None, ge=0)
    faturamento_periodo_brl: Optional[float] = Field(default=None, ge=0)
    resposta: str = Field(description="Texto amigável pro usuário final")

    @field_validator("estacao_id")
    @classmethod
    def formato_estacao(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.fullmatch(r"EST-\d{2,4}", v):
            raise ValueError("estacao_id deve seguir o padrão EST-XX (ex.: EST-01)")
        return v

    @field_validator("estado_carregador", mode="before")
    @classmethod
    def normaliza_estado(cls, v: object) -> object:
        # modelos às vezes devolvem "Disponível" ou "em manutenção" — padroniza aqui
        if isinstance(v, str):
            mapa = {
                "disponível": "disponivel",
                "disponivel": "disponivel",
                "livre": "disponivel",
                "ocupado": "ocupado",
                "em uso": "ocupado",
                "reservado": "reservado",
                "offline": "offline",
                "fora do ar": "offline",
                "manutenção": "manutencao",
                "manutencao": "manutencao",
                "em manutenção": "manutencao",
            }
            return mapa.get(v.strip().lower(), v)
        return v

    @field_validator("potencia_kw")
    @classmethod
    def potencia_plausivel(cls, v: float) -> float:
        # acima de 350 kW não existe em carregador veicular comercial hoje
        if v > 350:
            raise ValueError("potência acima do plausível para carregador veicular")
        return v
