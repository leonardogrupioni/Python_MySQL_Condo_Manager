import os
import streamlit as st
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from db import SessionLocal, Base, engine
from models import Apartamento, Morador, Despesa, Pagamento, Notificacao
from security import hash_pwd, check_pwd
import reports
from contextlib import contextmanager

Base.metadata.create_all(bind=engine)

# Helpers
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Auth
def login_user(db, email, pwd):
    user = db.query(Morador).filter(Morador.email == email).first()
    if user and check_pwd(pwd, user.senha_hash):
        return user

def sidebar_user_info(user):
    st.sidebar.success(f"Olá, {user.nome} ({user.papel})", icon="👤")

# Paginas
def page_apartamentos(db):
    st.header("🏢 Apartamentos")
    data = db.query(Apartamento).all()
    st.dataframe([{**a.__dict__} for a in data], hide_index=True, use_container_width=True)

    with st.expander("➕ Novo Apartamento"):
        col1, col2, col3 = st.columns(3)
        numero = col1.text_input("Número")
        bloco  = col2.text_input("Bloco")
        andar  = col3.number_input("Andar", step=1, format="%d")
        if st.button("Criar"):
            apt = Apartamento(numero=numero, bloco=bloco, andar=andar)
            db.add(apt)
            try:
                db.commit()
                st.success("Apartamento criado!")
                st.experimental_rerun()
            except IntegrityError:
                db.rollback()
                st.error("Número + Bloco deve ser único")

def page_moradores(db):
    st.header("👥 Moradores")

    #listagem
    moradores = (
        db.query(Morador)
          .options(selectinload(Morador.apartamento))
          .all()
    )

    st.dataframe([{
        "ID": m.id,
        "Nome": m.nome,
        "Email": m.email,
        "Telefone": m.telefone,
        "Profissao": m.profissao,
        "Papel": m.papel,
        "Apartamento": (
            f"{m.apartamento.numero}-{m.apartamento.bloco}"
            if m.apartamento else "-"
        )
    } for m in moradores], hide_index=True, use_container_width=True)

    with st.expander("➕ Novo Morador"):
        nome_new  = st.text_input("Nome", key="nome_new")
        email_new = st.text_input("Email", key="email_new")
        tel_new   = st.text_input("Telefone", key="tel_new")
        profissao_new   = st.text_input("Profissao", key="profissao_new")
        senha_new = st.text_input("Senha", type="password", key="senha_new")
        papel_new = st.selectbox("Papel",
                                 ["MORADOR", "SINDICO"],
                                 key="papel_new")

        aptos = db.query(Apartamento).all()
        if aptos:
            apt_sel_new = st.selectbox(
                "Apartamento",
                aptos,
                format_func=lambda a: f"{a.numero}-{a.bloco}",
                key="apt_new"
            )
            apt_id_new = apt_sel_new.id
        else:
            st.warning("Cadastre um apartamento antes.")
            apt_id_new = None

        if st.button("Cadastrar", key="btn_create"):
            if not nome_new or not email_new or not senha_new:
                st.error("Preencha nome, e-mail e senha.")
                st.stop()

            user = Morador(
                nome=nome_new,
                email=email_new,
                telefone=tel_new,
                profissao=profissao_new,
                senha_hash=hash_pwd(senha_new),
                papel=papel_new,
                apartamento_id=apt_id_new
            )
            db.add(user)
            try:
                db.commit()
                st.success("Morador cadastrado!")
                st.experimental_rerun()
            except IntegrityError:
                db.rollback()
                st.error("E-mail já existente.")

    # editar e excluir
    with st.expander("✏️ Editar ou Excluir Morador"):
        if not moradores:
            st.info("Nenhum morador cadastrado ainda.")
            st.stop()

        alvo = st.selectbox(
            "Selecione o morador",
            moradores,
            format_func=lambda m: f"{m.id} – {m.nome}",
            key="morador_select"
        )

        # campos editáveis
        nome_edit  = st.text_input("Nome", value=alvo.nome, key="nome_edit")
        email_edit = st.text_input("Email", value=alvo.email, key="email_edit")
        tel_edit   = st.text_input("Telefone", value=alvo.telefone, key="tel_edit")
        profissao_edit = st.text_input("Profissao", value=alvo.profissao, key="profissao_edit")
        papel_edit = st.selectbox(
            "Papel",
            ["MORADOR", "SINDICO"],
            index=1 if alvo.papel == "SINDICO" else 0,
            key="papel_edit"
        )

        aptos = db.query(Apartamento).all()
        if aptos:
            apt_idx = next(
                (i for i, a in enumerate(aptos)
                 if a.id == (alvo.apartamento_id or 0)),
                0
            )
            apt_sel_edit = st.selectbox(
                "Apartamento",
                aptos,
                index=apt_idx,
                format_func=lambda a: f"{a.numero}-{a.bloco}",
                key="apt_edit"
            )
            apt_id_edit = apt_sel_edit.id
        else:
            st.warning("Sem apartamentos cadastrados.")
            apt_id_edit = None

        col1, col2 = st.columns(2)

        # salvar alterações 
        if col1.button("💾 Salvar alterações", key="btn_update"):
            alvo_db = db.get(Morador, alvo.id) 

            alvo_db.nome     = nome_edit
            alvo_db.email    = email_edit
            alvo_db.telefone = tel_edit
            alvo_db.profissao = profissao_edit
            alvo_db.papel    = papel_edit
            alvo_db.apartamento_id = apt_id_edit

            try:
                db.commit()
                st.success("Morador atualizado!")
                st.experimental_rerun()
            except IntegrityError:
                db.rollback()
                st.error("E-mail já existente para outro morador.")

        # excluir
        if col2.button("🗑️ Excluir morador", key="btn_delete"):
            alvo_db = db.get(Morador, alvo.id)
            db.delete(alvo_db)
            db.commit()
            st.warning("Morador removido.")
            st.experimental_rerun()
            
def page_despesas(db, user):
    st.header("💰 Despesas")
    data = db.query(Despesa).options(selectinload(Despesa.apartamento)).all()
    st.dataframe([{
        "ID": d.id,
        "Descrição": d.descricao,
        "Valor": float(d.valor),
        "Vencimento": d.vencimento,
        "Pago": d.pago,
        "Apartamento": f"{d.apartamento.numero}-{d.apartamento.bloco}" if d.apartamento else "-"
    } for d in data], hide_index=True, use_container_width=True)

    with st.expander("➕ Registrar Despesa"):
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        venc = st.date_input("Vencimento", value=date.today())
        aptos = db.query(Apartamento).all()
        apt_sel = st.selectbox(
            "Apartamento", aptos,
            format_func=lambda a: f"{a.numero}-{a.bloco}"
        )
        if st.button("Lançar"):
            d = Despesa(descricao=desc, valor=valor, vencimento=venc, apartamento_id=apt_sel.id)
            db.add(d); db.commit(); st.experimental_rerun()

    st.subheader("Quitar Despesa")
    desp_id = st.number_input("ID da despesa", step=1, format="%d")
    if st.button("Quitar agora"):
        desp = db.get(Despesa, desp_id)
        if desp and desp.pago == "NAO":
            desp.pago = "SIM"
            pg = Pagamento(despesa=desp, morador=user, valor_pago=desp.valor)
            db.add(pg); db.commit(); st.success("Despesa quitada!")
            st.experimental_rerun()
        else:
            st.error("Despesa inexistente ou já paga")

    with st.expander("📄 Exportar despesas"):
        formato = st.radio("Formato", ["CSV", "PDF"], horizontal=True)
        if st.button("Gerar" ):
            deps = db.query(Despesa).options(selectinload(Despesa.apartamento)).all()
            path = reports.despesas_csv(deps) if formato == "CSV" else reports.despesas_pdf(deps)
            with open(path, "rb") as fh:
                st.download_button(
                    "Baixar",
                    data=fh,
                    file_name=os.path.basename(path),
                    mime="application/octet-stream"
                )

def page_notificacoes(db, user):
    st.header("🔔 Notificações")
    if user.papel == "SINDICO":
        with st.expander("➕ Enviar Notificação"):
            moradores = db.query(Morador).filter(Morador.id != user.id).all()
            alvo = st.selectbox("Morador", moradores, format_func=lambda m: m.nome)
            titulo = st.text_input("Título")
            msg = st.text_area("Mensagem")
            if st.button("Enviar"):
                notif = Notificacao(
                    morador_id = alvo.id, # usa apenas a chave estrangeira
                    titulo     = titulo,
                    mensagem   = msg
                )
                db.add(notif)
                db.commit()
                st.success("Enviado!")
                st.experimental_rerun()
        st.subheader("📜 Histórico de notificações")
            # consulta todas as notificações, já trazendo o morador relacionado
        historico = (db.query(Notificacao)
                    .join(Morador)                  # JOIN para pegar nome
                    .order_by(Notificacao.criada_em.desc())
                    .all())

        st.dataframe([{
            "ID":    n.id,
            "Morador": n.morador.nome,
            "Título":  n.titulo,
            "Mensagem": n.mensagem,
            "Criada em": n.criada_em.strftime("%d/%m/%Y %H:%M"),
            "Lida?": "✅" if n.lida == "SIM" else "❌"
        } for n in historico],
            use_container_width=True,
            hide_index=True)
    else:
        notas = db.query(Notificacao).filter(Notificacao.morador == user).order_by(Notificacao.criada_em.desc()).all()
        st.dataframe([{
            "ID": n.id,
            "Título": n.titulo,
            "Mensagem": n.mensagem,
            "Criada em": n.criada_em,
            "Lida": n.lida
        } for n in notas], hide_index=True, use_container_width=True)

        not_id = st.number_input("ID para marcar lida", step=1, format="%d")
        if st.button("Marcar como lida"):
            n = db.get(Notificacao, not_id)
            if n and n.morador_id == user.id:
                n.lida = "SIM"; db.commit(); st.experimental_rerun()

# Main
st.set_page_config(page_title="Gestão de Condomínio", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

with get_db() as db:
    if st.session_state.user is None:
        st.title("🔑 Login")
        with st.form("login"):
            email = st.text_input("E-mail")
            pwd   = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                user = login_user(db, email, pwd)
                if user:
                    st.session_state.user = {k: getattr(user, k) for k in ("id","nome","papel")}
                    st.experimental_rerun()
                else:
                    st.error("Credenciais inválidas.")
        st.stop()

    user_dict = st.session_state.user
    user = db.get(Morador, user_dict["id"])
    sidebar_user_info(user)

    # Botão de logout
    if st.sidebar.button("Logout 🚪"):
        st.session_state.user = None
        st.experimental_rerun()

    menu = ["Apartamentos", "Moradores", "Despesas", "Notificações"]
    if user.papel != "SINDICO":
        menu = ["Notificações"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Apartamentos": page_apartamentos(db)
    elif choice == "Moradores": page_moradores(db)
    elif choice == "Despesas": page_despesas(db, user)
    else: page_notificacoes(db, user)
