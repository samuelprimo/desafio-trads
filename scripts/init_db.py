import os
import time
import pandas as pd
from sqlalchemy import create_engine, text

#configurações do banco
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "operadoras_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def wait_for_db():
    retries = 30
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("conexão com o banco estabelecida.")
            return engine
        except Exception:
            print("aguardando banco de dados...")
            time.sleep(2)
            retries -= 1
    raise Exception("erro crítico: não foi possível conectar ao banco.")


def clean_currency(value):
    if pd.isna(value):
        return 0.0
    #remove formatação PT-BR e aspas residuais
    str_val = str(value).replace('"', '').replace("'", "").strip()
    str_val = str_val.replace('.', '').replace(',', '.')
    try:
        return float(str_val)
    except ValueError:
        return 0.0


def clean_quotes(value):
    if pd.isna(value):
        return value
    return str(value).replace('"', '').replace("'", "").strip()


def init_db():
    engine = wait_for_db()

    print("processando carga de dados.......")
    df = pd.read_csv('/app/operadoras_ficticias.csv',
                     delimiter=';', encoding='utf-8')

    #padronização de nomes de colunas para o backend
    mapa_colunas = {
        "0-18": "faixa_0_18", "19-23": "faixa_19_23", "24-28": "faixa_24_28",
        "29-33": "faixa_29_33", "34-38": "faixa_34_38", "39-43": "faixa_39_43",
        "44-48": "faixa_44_48", "49-53": "faixa_49_53", "54-58": "faixa_54_58",
        "59+": "faixa_59_mais", "59 +": "faixa_59_mais"
    }
    df.rename(columns=mapa_colunas, inplace=True)

    #tratamento de valores monetários
    cols_monetarias = [c for c in df.columns if 'faixa_' in c]
    for col in cols_monetarias:
        df[col] = df[col].apply(clean_currency)

    #limpeza da coluna identificadora de vidas
    if 'vidas' in df.columns:
        df['vidas'] = df['vidas'].apply(clean_quotes)

    print("salvando registros no banco........")
    df.to_sql('planos', engine, if_exists='replace', index=False)

    #otimização de performance
    with engine.connect() as conn:
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_vidas ON planos(vidas);"))
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_estado ON planos(estado);"))
        conn.commit()

    print(f"setup concluído. {len(df)} registros importados.")


if __name__ == "__main__":
    init_db()
