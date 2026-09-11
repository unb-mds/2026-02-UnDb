from app.db.session import engine, Base
import app.models  # carrega todas as tabelas registradas

if __name__ == "__main__":
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")