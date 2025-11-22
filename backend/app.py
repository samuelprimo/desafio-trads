import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware

#configuração do banco de dados
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "operadoras_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #eu sei que é perigoso em produção real
    allow_methods=["*"],
    allow_headers=["*"],
)


class CotacaoRequest(BaseModel):
    vidas: int
    faixas_etarias: List[str]
    estado: Optional[str] = None


def mapear_vidas(qtd: int) -> str:
    if qtd <= 2:
        return "2"
    elif 3 <= qtd <= 29:
        return "3 a 29"
    elif 30 <= qtd <= 99:
        return "30 a 99"
    elif 100 <= qtd <= 199:
        return "100 a 199"
    return None


def mapear_faixa_etaria_coluna(faixa_str: str) -> str:
    mapa = {
        "0-18": "faixa_0_18", "19-23": "faixa_19_23", "24-28": "faixa_24_28",
        "29-33": "faixa_29_33", "34-38": "faixa_34_38", "39-43": "faixa_39_43",
        "44-48": "faixa_44_48", "49-53": "faixa_49_53", "54-58": "faixa_54_58",
        "59+": "faixa_59_mais"
    }
    return mapa.get(faixa_str)


def calcular_score(plano, req, max_ativos):
    """calcula score de recomendação (0 a 1) baseado na heurística de popularidade."""
    score = 0.0

    #popularidade (Peso 40%)
    if max_ativos > 0:
        score += (plano['quantidade_de_ativos'] / max_ativos) * 0.4

    #compatibilidade de perfil (Peso 30%)
    score += 0.3

    #competitividade de preço (Peso 20%)
    score += 0.1

    #regionalidade (Peso 10%)
    if req.estado and plano['estado']:
        if req.estado.strip().upper() in str(plano['estado']).strip().upper():
            score += 0.1

    return round(score, 2)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/cotacao")
def criar_cotacao(req: CotacaoRequest):
    vidas_str = mapear_vidas(req.vidas)
    if not vidas_str:
        raise HTTPException(
            status_code=400, detail="Quantidade de vidas não suportada")

    with engine.connect() as conn:
        #obttém máximo de ativos para normalização do score
        max_ativos = conn.execute(
            text("SELECT MAX(quantidade_de_ativos) FROM planos")).scalar() or 1

        #busca baseada na quantidade de vidas
        query = text("SELECT * FROM planos WHERE vidas = :vidas")
        result = conn.execute(query, {"vidas": vidas_str})
        planos_raw = result.mappings().all()

    planos_processados = []

    for row in planos_raw:
        plano_dict = dict(row)

        #filtro de Estado (Case Insensitive)
        if req.estado:
            estado_banco = str(plano_dict.get('estado', '')).strip().upper()
            estado_req = req.estado.strip().upper()

            if estado_req not in estado_banco:
                continue

        valor_total = 0.0
        detalhes_vidas = []

        #cálculo do valor total somando por faixa etária
        for faixa in req.faixas_etarias:
            coluna = mapear_faixa_etaria_coluna(faixa)
            if coluna:
                valor = float(plano_dict.get(coluna, 0))
                valor_total += valor
                detalhes_vidas.append({"faixa": faixa, "valor": valor})

        plano_dict["valor_total"] = round(valor_total, 2)
        plano_dict["valores_por_vida"] = detalhes_vidas

        #cálculo de Score e Recomendação
        score = calcular_score(plano_dict, req, max_ativos)
        plano_dict["score_recomendacao"] = score
        plano_dict["recomendado"] = score > 0.6

        planos_processados.append(plano_dict)

    #ordenação: Primeiro por recomendação (score), depois por menor preço
    planos_processados.sort(
        key=lambda x: (-x["score_recomendacao"], x["valor_total"]))

    return {
        "success": True,
        "total": len(planos_processados),
        "planos": planos_processados,
        "planos_recomendados": planos_processados[:3]
    }
