from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from auth import hash_senha, verificar_senha

app = FastAPI()

Base.metadata.create_all(bind=engine)

# ======================
# DEPENDÊNCIA DB
# ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================
# AUTH
# ======================
@app.post("/register")
def register(usuario: str, senha: str, db: Session = Depends(get_db)):
    user = models.Usuario(usuario=usuario, senha=hash_senha(senha))
    db.add(user)
    db.commit()
    return {"msg": "ok"}

@app.post("/login")
def login(usuario: str, senha: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter_by(usuario=usuario).first()
    if not user or not verificar_senha(senha, user.senha):
        raise HTTPException(status_code=400, detail="Erro login")
    return {"user_id": user.id}

# ======================
# FAZENDAS
# ======================
@app.post("/fazenda")
def criar_fazenda(nome: str, user_id: int, db: Session = Depends(get_db)):
    f = models.Fazenda(nome=nome, usuario_id=user_id)
    db.add(f)
    db.commit()
    return {"msg": "ok"}

@app.get("/fazendas/{user_id}")
def listar_fazendas(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Fazenda).filter_by(usuario_id=user_id).all()

# ======================
# TALHÕES
# ======================
@app.post("/talhao")
def criar_talhao(nome: str, area: float, fazenda_id: int, db: Session = Depends(get_db)):
    t = models.Talhao(nome=nome, area=area, fazenda_id=fazenda_id)
    db.add(t)
    db.commit()
    return {"msg": "ok"}

@app.get("/talhoes/{fazenda_id}")
def listar_talhoes(fazenda_id: int, db: Session = Depends(get_db)):
    return db.query(models.Talhao).filter_by(fazenda_id=fazenda_id).all()