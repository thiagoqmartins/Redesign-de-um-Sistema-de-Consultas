# createZZ.py
import os
import sys
import json
import sqlite3
import traceback

# ======= Força UTF-8 no stdout/stderr =======
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ======= Import do conector SAP =======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar  # noqa: E402


def limpar_sessao(session):
    """Limpa a sessão SAP de forma segura."""
    if not session:
        return
    try:
        # Fecha popups
        try:
            while session.Children.Count > 1:
                try:
                    session.findById("wnd[1]").close()
                except Exception:
                    break
        except Exception:
            pass

        # Volta para a tela inicial
        try:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            # print("Sessao SAP limpa (/n).", file=sys.stderr)
        except Exception as e:
            print(f"Erro ao enviar /n: {e}", file=sys.stderr)

    except Exception as e:
        print(f"Erro ao limpar sessao SAP: {e}", file=sys.stderr)


def ver_qtd():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'BD', 'banco_dados.db'))
    
    # print(f"Iniciando ver_qtd... DB: {DB_PATH}", file=sys.stderr)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome_resp FROM responsaveis")
    linhas = cursor.fetchall()
    
    # print(f"Total de responsaveis: {len(linhas)}", file=sys.stderr)
    
    session = None
    usuarios_processados = 0
    usuarios_com_erro = 0
    
    try:
        # Conecta UMA VEZ antes do loop
        session = conectar()
        if not session:
            raise Exception("Nao foi possivel conectar ao SAP (session=None).")
        
        # print("Sessao SAP obtida com sucesso", file=sys.stderr)
        
        # Processa cada responsável
        for linha in linhas:
            userSAP = linha[0]
            
            try:
                # print(f"Processando usuario: {userSAP}", file=sys.stderr)
                
                # Navegação SAP
                session.findById("wnd[0]/tbar[0]/okcd").text = "/niqs9"
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL").select()
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/chkDY_RST").selected = True
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/chkDY_MAB").selected = True
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/chkDY_IAR").selected = True
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/chkDY_OFN").selected = True
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/radDAT_YEAR").select()
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/radDAT_ALL").select()
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/ctxtPARNR_MA").text = userSAP
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/ctxtQMDAT-LOW").text = "01.10.2025"
                session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_ALL/ssub%_SUBSCREEN_TASK:RIQSMEL2:0103/btn%_QMART_%_APP_%-VALU_PUSH").press()
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "zz"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "zo"
                session.findById("wnd[1]/tbar[0]/btn[8]").press()
                session.findById("wnd[0]/usr/ctxtVARIANT").text = "//THIAGOQM"
                session.findById("wnd[0]/tbar[1]/btn[8]").press()
                session.findById("wnd[0]/tbar[0]/btn[0]").press()
                
                msgSystem = session.findById("wnd[0]/sbar").text
                total_linhas = 0
                
                # IMPORTANTE: captura o grid ANTES de limpar a sessão
                if msgSystem == "":
                    grid = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
                    total_linhas = grid.RowCount
                
                # print(f"Usuario {userSAP}: {total_linhas} atividades", file=sys.stderr)
                
                # Atualiza banco
                cursor.execute("""
                    UPDATE responsaveis
                    SET qtd_atividade = ?
                    WHERE nome_resp = ?
                """, (total_linhas, userSAP))
                conn.commit()
                
                usuarios_processados += 1
                
            except Exception as e:
                usuarios_com_erro += 1
                print(f"Erro ao processar {userSAP}: {e}", file=sys.stderr)
                # Continua para o próximo usuário
                
            finally:
                # Limpa a sessão DEPOIS de capturar os dados
                limpar_sessao(session)
        
        resultado = {
            "usuarios_processados": usuarios_processados,
            "usuarios_com_erro": usuarios_com_erro,
            "total": len(linhas)
        }
        
        # print(f"Concluido: {resultado}", file=sys.stderr)
        return 
        
    finally:
        # Fecha conexão do banco
        if conn:
            conn.close()
        
        # Limpa a sessão SAP ao final
        if session:
            limpar_sessao(session)


if __name__ == "__main__":
    try:
        resultado = ver_qtd()
        # Retorna JSON válido no stdout
        # print(json.dumps({"ok": True, "resultado": resultado}, ensure_ascii=False))
        # sys.exit(0)
    except Exception as e:
        # Retorna JSON de erro
        erro_json = {
            "ok": False,
            "erro": str(e),
            "tipo": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(json.dumps(erro_json, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)