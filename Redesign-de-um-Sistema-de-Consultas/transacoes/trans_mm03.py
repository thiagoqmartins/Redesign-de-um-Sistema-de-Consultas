def executar(session, numero_sap):    
    try:
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nmm03"
        
        session.findById("wnd[0]").sendVKey(0)       

        session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = numero_sap
        
        session.findById("wnd[0]").sendVKey(0)   

        descricao = session.findById("wnd[0]/usr/tabsTABSPR1/tabpSP01/ssubTABFRA1:SAPLMGMM:2004/subSUB1:SAPLMGD1:1002/txtMAKT-MAKTX").text

        return descricao
    except Exception as e:
        # print(f"❌ Erro ao executar MM03: {e}")
        return None