# Sistema de Cotação Inteligente de Planos de Saúde

Sistema Full Stack containerizado para cotação de planos de saúde com pipeline de ETL e algoritmo de recomendação baseado em dados.

## Tecnologias Utilizadas

- **Infraestrutura:** Docker & Docker Compose
- **Backend:** Python 3.11, FastAPI, Pydantic, SQLAlchemy
- **Frontend:** HTML5, Bootstrap 5, JavaScript (Vanilla), Nginx
- **Banco de Dados:** PostgreSQL 15
- **Processamento de Dados (ETL):** Pandas
- **Formatação e Estilo de Código:** autopep8

## Funcionalidades

1.  **Pipeline ETL Automático:** Script de inicialização que higieniza dados brutos (CSV), corrige formatações monetárias e normaliza o schema do banco.
2.  **Cotação Dinâmica:** Cálculo de preço baseado na matriz de Quantidade de Vidas x Faixas Etárias.
3.  **Sistema de Recomendação:** Algoritmo heurístico que pontua planos com base em popularidade, preço e regionalidade (Score de Compatibilidade).
4.  **Arquitetura de Microsserviços:** Serviços isolados para Banco, Backend e Frontend.

## Como Rodar o Projeto

### Pré-requisitos
- Docker Desktop instalado e rodando.

### Passo a Passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/samuelprimo/desafio-trads.git
   cd desafio-trads
