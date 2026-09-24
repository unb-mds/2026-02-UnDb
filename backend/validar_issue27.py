import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.services.sigaa_import_service import (
    executar_importacao, 
    DepartamentoImportacao
)

# String corrigida com os dados exatos do seu .env e mapeamento do Docker (porta 15432)
DATABASE_URL = "postgresql+psycopg2://g7:troque-por-uma-senha-local@localhost:15432/g7"
engine = create_engine(DATABASE_URL)

def rodar_amostra():
    with Session(engine) as db:
        departamentos = [
            DepartamentoImportacao(
                departamento="Ciência da Computação", 
                unidade_sigaa="DEPTO CIÊNCIAS DA COMPUTAÇÃO - BRASÍLIA"
            ),
            DepartamentoImportacao(
                departamento="Matemática", 
                unidade_sigaa="DEPARTAMENTO DE MATEMÁTICA - BRASÍLIA"
            ),
            DepartamentoImportacao(
                departamento="Física (Teste Falha)", 
                unidade_sigaa="DEPARTAMENTO INVENTADO PARA FALHAR"
            ) 
        ]
        
        print("A iniciar extração no SIGAA...")
        resultado = executar_importacao(db, departamentos, ano="2026", periodo="2")
        
        print("\n=== REGISTO DE EXECUÇÃO (RF19) ===")
        print(json.dumps(resultado.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    rodar_amostra()