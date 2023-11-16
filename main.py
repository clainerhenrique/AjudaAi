from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)

app = FastAPI()

#######################

# Configuração da conexão com o banco de dados MySQL
DATABASE_URL = "mysql+mysqlconnector://root:@127.0.0.1:3306/db_ajuda_ai"
engine = create_engine(DATABASE_URL)

# Criação da tabela de usuários no banco de dados
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(25), unique=True, index=True)
    cpf = Column(String(11), unique=True, index=True)
    senha = Column(String(25))

Base.metadata.create_all(bind=engine)

# Modelo de dados para o usuário
class UserCreate(BaseModel):
    nome: str
    cpf: str
    senha: str

class UserLogin(BaseModel):
    cpf: str
    senha: str

# Rota para criar um novo usuário
@app.post("/cadastrar_usuario/")
def create_user(user: UserCreate):
    # Verifique se o CPF já está em uso
    with engine.connect() as conn:
        existing_user = conn.execute(text(f"SELECT cpf FROM usuarios WHERE cpf = '{user.cpf}'")).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    # Insira o novo usuário no banco de dados
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()
    user_db = UserDB(nome=user.nome, cpf=user.cpf, senha=user.senha)
    db_session.add(user_db)
    db_session.commit()
    db_session.close()

    return {"Mensagem": "Usuário cadastrado com sucesso"}

# Rota para fazer o login
@app.post("/login/")
def login(user: UserLogin):
    with engine.connect() as conn:
        user_db = conn.execute(text(f"SELECT * FROM usuarios WHERE cpf = '{user.cpf}'")).first()

    if user_db is not None and user_db[3] == user.senha:
        return {"Mensagem": "Login bem-sucedido"}
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou senha incorreta")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
