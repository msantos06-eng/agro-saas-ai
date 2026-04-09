from passlib.hash import bcrypt

def hash_senha(senha):
    return bcrypt.hash(senha)

def verificar_senha(senha, hash):
    return bcrypt.verify(senha, hash)