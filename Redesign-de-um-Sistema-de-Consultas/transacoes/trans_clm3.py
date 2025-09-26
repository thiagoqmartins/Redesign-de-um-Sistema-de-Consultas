def executar(session, numero_sap):  

    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
    session.findById("wnd[0]").sendVKey(0)

    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = numero_sap
    session.findById("wnd[0]").sendVKey(0)

    return "Concluído"
