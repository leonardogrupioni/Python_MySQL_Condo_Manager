import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date

def despesas_csv(despesas, path="despesas.csv"):
    df = pd.DataFrame([{
        "ID": d.id,
        "Descrição": d.descricao,
        "Valor": float(d.valor),
        "Vencimento": d.vencimento,
        "Pago": d.pago,
        "Apartamento": d.apartamento.numero if d.apartamento else "-"
    } for d in despesas])
    df.to_csv(path, index=False)
    return path

def despesas_pdf(despesas, path="despesas.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, 800, f"Relatório de Despesas – {date.today().strftime('%d/%m/%Y')}")
    y = 770
    for d in despesas:
        linha = f"{d.id} – {d.descricao} – R$ {float(d.valor):.2f} – {d.vencimento}"
        c.setFont("Helvetica", 11)
        c.drawString(40, y, linha)
        y -= 18
        if y < 40:
            c.showPage(); y = 800
    c.save()
    return path
