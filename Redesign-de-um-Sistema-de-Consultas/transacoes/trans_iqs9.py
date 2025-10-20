import sqlite3
import sys
import os
import json
from datetime import datetime, timedelta
import json
import traceback

from flask import session

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar

def ok(payload=None): #Concluido
    print(json.dumps({"ok": True, "resultado": payload}, ensure_ascii=False))
    sys.exit(0)

def fail(msg, extra=None):#Concluido
    out = {"ok": False, "erro": str(msg)}
    if extra is not None:        
        out["detalhe"] = str(extra)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)

def get_db_path(): #Concluido
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.normpath(os.path.join(project_root, 'BD', 'banco_dados.db')) 
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

# from transacoes import trans_clm3]
# def executar(session):      

def executar():           
    
    session = conectar()    

    data_futura = datetime.now() + timedelta(days=365*10)
    data_formatada = data_futura.strftime("%d.%m.%Y")
           
    session.findById("wnd[0]/tbar[0]/okcd").text = "/niqs9"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_MY/ssub%_SUBSCREEN_TASK:RIQSMEL2:0102/radTAS_WORK").Select()    
    session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_MY/ssub%_SUBSCREEN_TASK:RIQSMEL2:0102/radDAT_ALL").select()   
    session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_MY/ssub%_SUBSCREEN_TASK:RIQSMEL2:0102/ctxtQMDAT-LOW").Text = "01.08.2009"    
    session.findById("wnd[0]/usr/tabsTABSTRIP_TASK/tabpTASK_MY/ssub%_SUBSCREEN_TASK:RIQSMEL2:0102/ctxtQMDAT-HIGH").Text = data_formatada
    session.findById("wnd[0]/usr/ctxtVARIANT").Text = "//THIAGOQM2"  
    session.findById("wnd[0]").sendVKey(8)
    grid = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
    nRow = grid.RowCount   

    lista_de_dados = []
    sequencia = sequencia_execucao()  

    for i in range(nRow):

        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(BASE_DIR, 'BD', 'banco_dados.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        notaClaim = tratar_texto(grid.GetCellValue(i, "QMNUM"))
        notaSequencia = tratar_texto(grid.GetCellValue(i, "QSMNUM"))        


        #LIMITAR DATA DE CONSULTAS, DEFINIR DATA DE CORTE PARA INICIAR O NOVO PROCESSO.
        dataCriacao = datetime.strptime(tratar_texto(grid.GetCellValue(i, "ERDAT")) , "%d.%m.%Y")  # string -> datetime
        dataCorte = datetime.strptime("01.09.2025","%d.%m.%Y")
       
        if  dataCriacao > dataCorte: 
            query = """
                SELECT * 
                FROM consultas_iqs9 
                WHERE numero_nota = ? AND numero_ordem = ?
            """

            cursor.execute(query, (notaClaim, notaSequencia))
            resultado = cursor.fetchone()      

            nNota =  tratar_texto(grid.GetCellValue(i, "QSMNUM"))
            if nNota < "11":  
                if resultado:
                    sequencia = sequencia
                else:
                    sequencia = sequencia + 1  
                         
                linha = {
                    "tipo_nota": tratar_texto(grid.GetCellValue(i, "QMART")),
                    "numero_nota": tratar_texto(grid.GetCellValue(i, "QMNUM")),
                    "numero_ordem": tratar_texto(grid.GetCellValue(i, "QSMNUM")),
                    "cliente": tratar_texto(grid.GetCellValue(i, "KUNUM")),                 
                    "nome_lista": tratar_texto(grid.GetCellValue(i, "NAME_LIST")),                   
                    "descricao": tratar_texto(grid.GetCellValue(i, "QMTXT")),                  
                    "texto_medida": tratar_texto(grid.GetCellValue(i, "KTXTCD")),
                    "inicio_desejado": tratar_texto(grid.GetCellValue(i, "STRMN")),
                    "fim_planejado": tratar_texto(grid.GetCellValue(i, "PSTER")),
                    "fim_desejado": tratar_texto(grid.GetCellValue(i, "PETER")),
                    "status": tratar_texto(grid.GetCellValue(i, "QSMSTTXT")),
                    "data_criacao": tratar_texto(grid.GetCellValue(i, "ERDAT")),
                    "criado_por": tratar_texto(grid.GetCellValue(i, "ERNAM")),
                    "notificador": tratar_texto(grid.GetCellValue(i, "QMNAM")),                      
                    "sequencia" : sequencia,
                }        
                lista_de_dados.append(linha)        
    criar_banco_e_inserir_dados(lista_de_dados, session=session)     

    return "Concluído_Iqs9"

def tratar_texto(texto):
    if texto is None:
        return ''
    try:       
        return str(texto).encode('latin1').decode('utf-8').strip().upper()
    
    except:
        return str(texto).strip().upper()
    
def criar_banco_e_inserir_dados(lista_de_dados, session):

    DB_PATH = get_db_path()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Criar tabela (se não existir) com chave composta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultas_iqs9 (
            tipo_nota TEXT,
            numero_nota TEXT,
            numero_ordem TEXT,
            cliente TEXT,
            nome_lista TEXT,
            descricao TEXT,
            texto_medida TEXT,
            inicio_desejado TEXT,
            fim_planejado TEXT,
            fim_desejado TEXT,
            status TEXT,
            data_criacao TEXT,
            criado_por TEXT,
            notificador TEXT,
            num_claimzz INTERGER,
            status_claimZZ TEXT,
            seq_exec INTEGER,              
            PRIMARY KEY (numero_nota, numero_ordem)
        )
    ''') 

    # Inserção dos dados
    for dado in lista_de_dados:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO consultas_iqs9 (
                    tipo_nota, numero_nota, numero_ordem, cliente, nome_lista, descricao, 
                    texto_medida, inicio_desejado, fim_planejado, fim_desejado, status, 
                    data_criacao, criado_por, notificador, seq_exec
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dado["tipo_nota"],
                dado["numero_nota"],
                dado["numero_ordem"],
                dado["cliente"],
                dado["nome_lista"],
                dado["descricao"],
                dado["texto_medida"],
                dado["inicio_desejado"],
                dado["fim_planejado"],
                dado["fim_desejado"],
                dado["status"],
                dado["data_criacao"],
                dado["criado_por"],
                dado["notificador"],  
                dado["sequencia"]              
            ))
            # if cursor.rowcount == 1:
            #     buscar_dados(session=session, nota=dado["numero_nota"])                        
        except Exception as e:
            print(f"Erro ao inserir registro Nota: {dado['numero_nota']} Ordem: {dado['numero_ordem']} -> {e}")
    conn.commit()
    conn.close()

def sequencia_execucao():
    
    DB_PATH = get_db_path()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(MAX(seq_exec), 0) FROM consultas_iqs9
    """)

    maior_valor = cursor.fetchone()[0]
    return int(maior_valor)

if __name__ == "__main__":
    try:        
        resultado = executar() 
        print(json.dumps({"ok": True, "resultado": resultado}, ensure_ascii=False))
    except Exception as e:
        # Imprime JSON de erro válido
        erro_json = {
            "ok": False,
            "erro": str(e),
            "tipo": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(json.dumps(erro_json, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)  # exit code 1 para indicar erro
      

   
    




   

 
 