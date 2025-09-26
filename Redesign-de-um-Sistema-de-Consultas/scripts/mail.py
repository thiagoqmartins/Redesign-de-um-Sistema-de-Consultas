import win32com.client  # ❌ externo — instalar com: pip install pywin32

def abrir_email_outlook(destinatario, assunto, corpo, nome_em_nome_de):
    outlook = win32com.client.Dispatch("Outlook.Application")
    email = outlook.CreateItem(0)  # 0 = olMailItem
    email.To = destinatario
    email.Subject = assunto
    email.Body = corpo
    email.SentOnBehalfOfName = nome_em_nome_de      
    email.send() # Abre a janela do email no Outlook

if __name__ == "__main__":
    try:
        abrir_email_outlook(
            "thiagoqm@weg.net",
            assunto="Assunto do E-mail",
            corpo="Aqui está o corpo do e-mail.",
            nome_em_nome_de="wtb-szo-eng@weg.net"
        )
        print("Concluído")
    except Exception as e:
        print("Erro:", e)
