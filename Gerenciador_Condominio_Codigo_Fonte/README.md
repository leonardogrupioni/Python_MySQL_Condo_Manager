# Sistema de Gerenciamento de Condomínio

Monólito **Python + Streamlit + MySQL** (inspirado no uCondo) — projeto da disciplina de Banco de Dados.

## Integrantes do Grupo:
| Nº | Nome                                      | RA         |
|----|-------------------------------------------|------------|
| 1  | Leonardo Fajardo Grupioni                 | RA00319703 |

## Estrutura 

```
condo_app/
├── venv              # Ambiente containerizado/venv
├── app.py
├── db.py
├── init_db.py        # cria tabelas e um síndico padrão
├── models.py
├── reports.py
├── security.py
├── schema.sql        # script DDL completo
└── requirements.txt
```

## Pré‑requisitos
* Python ≥ 3.9  
* MySQL ≥ 8  

## Passo a Passo

```bash
# 1) clonar / copiar pasta
cd condo_app

# 2) criar venv
python -m venv venv
source venv/bin/activate      
# (Windows) 
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   venv\Scripts\activate

# 3) instalar dependências
pip install -r requirements.txt

# 4) criar base + tabelas e síndico
mysql -u root -p < schema.sql     # usa suas credenciais (senha)
# caso nao funcione use:
# & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" `
#     -u root -p `
#     -e "source schema.sql"
python init_db.py                 # gera usuário admin

# 5) editar DB_URL (caso mude) em db.py

# 6) rodar aplicação
streamlit run app.py
```

Logar com:
```
E‑mail: admin@condo.local
Senha : 1234
```

## Funcionalidades demonstradas

| Tema | Ponto |
|------|-------|
| Modelagem & FK | apartamento, morador, despesa, pagamento… |
| SQLAlchemy ORM | camadas de persistência |
| Autenticação segura | `bcrypt` |
| Geração de relatórios | CSV e PDF |
| Interface Streamlit | CRUD, download, uploads futuros |
