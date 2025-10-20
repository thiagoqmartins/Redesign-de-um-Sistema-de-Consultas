
import sys
import win32com.client  # ❌ externo — instalar com: pip install pywin32
import re
import json
import subprocess
import time
from scripts.connectSAP import conectar


# Força o uso de UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')


#TAG       → Classificação
#NT        → Novas Turbinas
#NR        → Novos Redutores
#ST        → Serviços Turbinas
#SR        → Serviços Redutores
#GT        → Gestão Projetos Turbinas
#GR        → Gestão Projetos Redutores
#GST       → Gestão Serviços Turbinas
#GSR       → Gestão Serviços Redutores
#AT-T      → Assistência Técnica Turbinas
#AT-R      → Assistência Técnica Redutores

#TAG       → Identificardor
#NT        → 1 
#NR        → 2 
#ST        → 3 
#SR        → 4 
#GT        → 5 
#GR        → 6 
#GST       → 7 
#GSR       → 8 
#AT-T      → 9 
#AT-R      → 10 

#TAG       → Quantidade Atividades
#NT        → 7 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos Redutor > Estudos Turbina > Documentação)
#NR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos Redutor > Documentação)
#ST        → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)
#SR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)
#GT        → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos > Documentação)
#GR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Documentação)
#GST       → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)    
#GSR       → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)
#AT-T      → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)
#AT-R      → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças)





# Processo de validação ?????

    
def dados_claim(nclaim): 

    session = conectar()    
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = nclaim
    session.findById("wnd[0]").sendVKey(0)
    descricaoClaim = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").text
    descricaoClaim = descricaoClaim.split()
    descricaoClaim = descricaoClaim[0]

  
    return descricaoClaim
    
