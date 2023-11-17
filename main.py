import statistics
from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pydantic import BaseModel, ValidationError
from fastapi import Depends, Form
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from fastapi import status
from fastapi.responses import RedirectResponse



app = FastAPI()

# Função para obter uma sessão do banco de dados
def get_db_session():
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()
    try:
        yield db_session
    finally:
        db_session.close()

# Rota principal para renderizar a página de login
@app.get("/", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Configuração para servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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

class UserLogin(BaseModel):
    cpf: str
    senha: str

    @validator("cpf")
    def validate_cpf(cls, value):
        # Adicione a lógica de validação do CPF conforme necessário
        # Aqui, um exemplo simples apenas para ilustração
        if not value.isdigit() or len(value) != 11:
            raise ValueError("CPF inválido")
        return value

# Modelo de dados para o usuário
class UserCreate(BaseModel):
    nome: str
    cpf: str
    senha: str

class UserLogin(BaseModel):
    cpf: str
    senha: str

# Rota principal para renderizar a página de login e cadastro
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, this is the main page"})

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

# Função para obter uma sessão do banco de dados
def get_db_session():
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = db()
    try:
        yield db_session
    finally:
        db_session.close()

templates = Jinja2Templates(directory="templates")

# Rota para a página de login bem-sucedido
@app.get("/login_success", response_class=HTMLResponse)
async def login_success(request: Request):
    return templates.TemplateResponse("login_success.html", {"request": request})

# Rota para fazer o login
@app.post("/login/")
def login(user: UserLogin, response: Response, session: Session = Depends(get_db_session)):
    try:
        # Adicione sua lógica de validação aqui se necessário

        with engine.connect() as conn:
            user_db = conn.execute(text(f"SELECT * FROM usuarios WHERE cpf = '{user.cpf}'")).first()

        if user_db is not None and user_db[3] == user.senha:
            # Aqui você pode adicionar lógica para criar uma sessão de usuário, se necessário
            # e redirecionar para outra página, ou simplesmente retornar uma mensagem de sucesso.
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie("user", user.cpf)  # Exemplo: definindo um cookie com o CPF do usuário
            return response
        else:
            raise HTTPException(status_code=401, detail="Usuário não encontrado ou senha incorreta")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

# Rota para redirecionar a rota /docs para a página principal
@app.get("/docs", include_in_schema=False)
async def redirect_to_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Redirecting to the main page..."})

# Configuração de templates
templates = Jinja2Templates(directory="templates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
