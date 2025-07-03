from db import SessionLocal, Base, engine
from models import Morador
from security import hash_pwd

def main():
    # Cria tabelas se ainda não existirem
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    # Verifica se já existe um síndico
    if not db.query(Morador).filter(Morador.papel == "SINDICO").first():
        admin = Morador(
            nome="Gru",
            email="admin@condo.local",
            senha_hash=hash_pwd("1234"),
            papel="SINDICO"
        )
        db.add(admin)
        db.commit()
        print("Usuário síndico criado (email: admin@condo.local / senha: 1234)")
    else:
        print("Síndico já existe, nada a fazer.")
    db.close()

if __name__ == "__main__":
    main()
