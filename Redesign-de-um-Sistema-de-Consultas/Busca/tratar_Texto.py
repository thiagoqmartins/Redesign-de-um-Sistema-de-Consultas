import re
import nltk
import spacy
# pip install spacy

from nltk.corpus import stopwords
# pip install nltk

from unidecode import unidecode
# pip install unidecode
# python -m spacy download pt_core_news_sm



# Baixar recursos necessários (apenas uma vez)
nltk.download('stopwords')
nlp = spacy.load('pt_core_news_sm')  # modelo português do spaCy

# Lista personalizada de palavras técnicas repetitivas
custom_stopwords = set([
    # Termos técnicos genéricos
    'redutor', 'acoplamento', 'eixo', 'engrenagem', 'carcaca', 'modelo', 'sistema',
    'documento', 'instalacao', 'montagem', 'lubrificacao', 'fixacao', 'desenho',
    'manual', 'operacao', 'manutencao', 'cronograma', 'esquema', 'massa',
    'transmissao', 'potencia', 'torque', 'relacao', 'rotacao', 'entrada', 'saida',
    'tipo', 'tamanho', 'norma', 'volume', 'vazao', 'quantidade', 'material',
    'chapa', 'aco', 'rolamento', 'sapata', 'retentor', 'viton', 'parte', 'item',

    # Unidades e siglas técnicas
    'rpm', 'kw', 'nm', 'mm', 'kgf', 'l', 'cst', 'pdf', 'iso', 'vg', 'ep', 'din',
    'doc', 'os', 'crnimo', 'sae', 'astm',

    # Atributos redundantes ou genéricos
    'sim', 'nao', 'alto', 'baixo', 'oposto', 'existente', 'adicional', 'identico',
    'intercambiavel', 'conforme', 'aproximado', 'conf', 'segundo', 'medida',

    # Termos administrativos
    'dados', 'informacao', 'comentario', 'elaboracao', 'proposta', 'venda',
    'industrial', 'cliente', 'responsabilidade', 'departamento', 'qualidade',
    'indice', 'frete', 'comissao', 'valor', 'custo', 'analise', 'analisar',
    'aplicar', 'revisar', 'verificar', 'finalizada', 'atentar', 'solicitar',
    'inserir', 'utilizado', 'utilizar', 'seguem', 'seguir',

    # Palavras comuns genéricas
    'bom', 'gentileza', 'saudacoes', 'caso', 'favor', 'tgm', 'engapl', 'engindustr',
    'comerc', 'bento', 'thiago', 'roger', 'jair',

    # Marcas de formatação
    'linha', 'texto', 'campo', 'indice', 'nome', 'condicoe', 'roteiro', 'pintura',
    'teste', 'embalagem', 'materia', 'primo', 'respiro', 'filtro', 'tampa',

    # Outras
    'o', 'em', "a", 'dia', 'tarde', 'noite', 'Martins', 'parteobjet', 'causa', 'etc',
    'natalia', 'Scaranello', 'perticarrari'
])


# Stopwords gerais
stop_words = set(stopwords.words('portuguese')).union(custom_stopwords)

def preprocess_text(text):
    # Remover pontuação, símbolos e unidades
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+[:;/\-]*', '', text)
    text = unidecode(text.lower())

    # Tokenizar e lematizar
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if token.lemma_ not in stop_words and not token.is_space and len(token.lemma_) > 2]

    return ' '.join(tokens)

# Exemplo de uso
texto_original = "Bom dia, Solcito calculo de redutor conforme informações abaixo e em anexo, para substitui um redutor paralelo Flender H2SH 25: - Acionada: Motor 50Hz 6P - Acionamento: Moinho de bolas - Potencia: 6.000 kW - Rotação entrada: 990 rpm - Rotação saída: 136,3 rpm - Relação transmissão: 7,26 Favor, elaboara também planilha de custo. Nenhuma ação existente Medida para Thiago Martins: ENGAPL-ENG. APLIC. ANALISAR REFERENCIAS (CUSTOS E ESTUDO): ZFE 10012482463 000 00 Planilha Escopo Custos - 422371288 #INDUSTRIAL, VERIFICAR CONSULTA SEMELHANTE RESPONDIDA EM 2022: CLAIM - 419924876 #VENDAS: - NÃO CONSIDERADO EQUIPAMENTO INTERCAMBIAVEL - NÃO CONSIDERADO FORNECIMENTO DE UNIDADE HIDRAULICA - NÃO CONSIDERADO FORNECIMENTO DE ACOPLAMENTO (ENTRADA OU SAIDA) - NÃO CONSIDERADO ITENS DE INSTALAÇÃO (PLACAS, TIRANTES, NIVELADORES, ETC..) ----------------------------- DADOS TECNICOS –-------------------------- Tipo Redutor...........................: Eixos Paralelos de Múltiplos Estágios Modelo.................................: RSN Y2 1000 Tamanho................................: 1000 Relação de Transmissão.................: 7,26:1 Rotação de Entrada.....................: 990 RPM Rotação de Saída.......................: 136,29 RPM Potência Nominal.......................: - Potência Instalada.....................: 6.000 kW Potência de Trabalho...................: HOLD Torque Entrada.........................: ~57.900,00 Nm Torque Saída...........................: ~408.122,00 Nm Torque de Trabalho.....................: HOLD Fator de Serviço (p/i).................: 2,16 Fator de Serviço (t/n).................: - Volume de Óleo estimado................: HOLD Vazão de óleo estimada.................: ~ (HOLD) L/min. Tipo de Óleo...........................: ISO VG 220 EP cSt / 40°C Qtd. de calor a ser retirado...........: HOLD Massa estimada.........................: ~26.000 kg Vida Teórica dos Rolamentos ...........: HOLD Normas p/ Calc. e Seleção conforme.....: IT-EN-059 --------------------------- DADOS ADICIONAIS --------------------------- Disposição Eixos (Baixa)...............: Paralelo Disposição Horizontal Sentido Giro (Alta)....................: Anti-Horário Sentido Giro (Baixa)...................: O mesmo que o de alta Ventilador.............................: Não Trocador de Calor......................: Sim Carcaça Aletada........................: Não Material Eixo (Alta)...................: Aço-liga 18CrNiMo7-6 Material Eixo (Baixa)..................: Aço SAE 4340 Material Engrenagem....................: Aço-liga 18CrNiMo7-6 Material Carcaça.......................: Aço ASTM A36 Sistema de Vedação.....................: Retentores em Viton + Tampas Taconite Mancal Tipo (Rolamento/Deslizamento)...: Rolamento Tipo de Fixação........................: Base civil ------------------------------ INTERFACES ------------------------------ Tipo Eixo de Alta......................: Ponta cilíndrica chavetada (DIN 6885) Qta Eixos..............................: 1 Tipo Eixo de Baixa.....................: Ponta cilíndrica chavetada (DIN 6885) Qta Eixos..............................: 1 Roscas Sensor Temperatura..............: Não Roscas Sensor Vibração.................: Não Roscas Sensor Acelerômetro.............: - ------------------------------ ACESSORIOS ------------------------------ Acoplamento de Alta....................: Não Acoplamento de Baixa...................: Não Sistema Contra Recuo...................: Não Braço de torque........................: Não Itens de fixação do braço de torque....: Não Placas de assentamento / nivelamento...: Não Itens de fixação da placa..............: Não Itens de fixação do pé.................: Não Suporte para motor.....................: Não Flange do motor........................: Não Eixo tipo cardan.......................: Não Proteção para cardan...................: Não Proteção acoplamento de alta...........: Não Proteção acoplamento de baixa..........: Não Sistema de proteção principal..........: Não Sistema de proteção adicional..........: Não Bomba de lubrificação..................: Não Bomba de lubrificação (auxiliar).......: Não Bomba de lubrificação (emergência).....: Não Giro lento.............................: Não Sistema de engate \\\"Giro Lento\\\".........: Não Respiro/Filtro de ar...................: Sim (tipo HDA) Tampa de inspeção......................: Sim Sistema de lubrificação interna........: Não Interligação unidade hidráulica........: Não Unidade hidráulica.....................: Não Trocador de calor......................: Não Roda de polos..........................: Não Unidade de controle de sujidade do óleo: Não ----------------------------- DOCUMENTACAO ----------------------------- • Desenho de instalação; • Desenho de montagem; • Esquema de alinhamento; • Cronograma de fabricação; • Tabela de alinhamento; • Esquema de massas; • Manual de instruções, operação e manutenção; • Data Book; Nota: todos em formato eletrônico (*.pdf) no idioma Inglês. -------------------- INFORMACOES PARA SUPRIMENTOS --------------------- • Cotar os itens destacados em verde na planilha anexa. --------------------- INFORMACOES PARA INDUSTRIAL --------------------- • Informar os tempos de operações dos itens destacados, bem como matéria-prima, montagem, pintura e testes e embalagem na planilha anexa; ----------------------- INFORMACOES PARA VENDAS ----------------------- • Solicitar PIT ao departamento de qualidade; • Devido se tratar de um equipamento fora de nossa linha padrão, recomendo prever um adicional de, pelo menos,5% de contingente no custo; Medida para Natalia Scaranello Perticarrari: TGM-SUPRIM-ANALISAR/ESPECIFICAR TR . ROLAMENTO 22348C3 W20 NSK/FAG/SKF - R$ 20.025,50 240 dias ROLAMENTO 23264 E NSK/FAG/SKF - R$ 31.266,00 240 dias ROLAMENTO 23080 CC/W33 NSK/FAG/SKF - R$ 20.238,03 240 dias Medida para Marcos Rodrigues Passos: TGM-ENGINDUSTR-ANALISAR/ESPECIFI TR Elaboração de custos conforme documento ZEI-10012498121. Medida para Rudinei Hannemann: TGM-CUSTOS-ANALISAR/ESPECIFICAR TR Não incluso Índice RKP, Adm. Vendas, frete e comissão. **** Caso identifique alguma divergência de valores por favor nos comunique***SE ATENTAR NO CAMPO COMENTÁRIOS GERAIS*** Calculo de custo conforme DOC.10012507676 Medida para Adriano da Cruz Filho: TGM-COMERC- ANALISAR/ESPECIF REDUTO . Cotar Unidade Hdráulica AR / Óleo para atender potência dissipada de 127.000 kcal/h. - Óleo mineral ISO VG 320. Medida para Adriano da Cruz Filho: TGM-COMERC- ANALISAR/ESPECIF REDUTO Status: Medida concluída ParteObjet Causa Custos"
texto_limpo = preprocess_text(texto_original)
print(texto_limpo)


# import spacy
# from collections import Counter
# from unidecode import unidecode
# import re

# # Carrega o modelo de linguagem
# nlp = spacy.load("pt_core_news_sm")

# def limpar_texto(texto):
#     texto = "Boa tarde. Por gentileza calcular e emitir planilha para custos de redutor reserva para a OS 48.01346 Modelo CSR 500. Verificar intercambialidade. Escopo: Redutor + Acoplamentos Nenhuma ação existente Medida para Thiago Martins: ENGAPL-ENG. APLIC. ANALISAR Saudações! Seguem informações para elaboração da proposta: 10012435358 ZFE - Planilha Escopo Custos_CSR 450 ---------------------------- DADOS TECNICOS ---------------------------- Tipo Redutor...........................: Eixos paralelos múltiplos estágios Modelo.................................: CSR 450 Tamanho................................: 450 Relação de Transmissão.................: 89,6:1 Rotação de Entrada.....................: 1.180 RPM Rotação de Saída.......................: 13,6 RPM Potência Nominal.......................: - Potência Instalada.....................: 110 kW Potência de Trabalho...................: HOLD Torque Entrada.........................: ~890 Nm Torque Saída...........................: ~76.230 Nm Torque de Trabalho.....................: HOLD Fator de Serviço (p/i).................: 2 Fator de Serviço (t/T).................: - Volume de Óleo.........................: 300 l Vazão de óleo aproximada...............: - Tipo de Óleo...........................: ISO VG 220 EP cSt/40°C Quantidade de calor a ser retirada.....: - Normas p/ Calc. e Seleção conforme.....: IT-EN-059 Massa aproximada.......................: ~3.720 kgf --------------------------- DADOS ADICIONAIS --------------------------- Disposição Eixos (Baixa)...............: (conf. O.S. 4801346) Sentido Giro (Alta)....................: (conf. O.S. 4801346) Sentido Giro (Baixa)...................: Oposto ao de alta Ventilador.............................: Não Trocador de Calor......................: Não Carcaça Aletada........................: Não Material Eixo (Alta)...................: Aço-liga 18CrNiMo7-6 Material Eixo (Baixa)..................: Aço SAE 4140 Material Engrenagem....................: Aço-liga 18CrNiMo7-6 Material Carcaça.......................: Chapa de aço ASTM A-36 Sistema de Vedação.....................: Retentor em Viton Mancal Tipo (Rolamento/Deslizamento)...: Rolamento Tipo de Fixação........................: Sapatas ------------------------------ INTERFACES ------------------------------ Tipo Eixo de Alta......................: Ponta cilíndrica chavetada DIN 6885 Qta Eixos..............................: 1 Dimensões Eixo de Alta.................: Ø55 x 90mm Tipo Eixo de Baixa.....................: Ponta cilíndrica chavetada DIN 6885 Qta Eixos..............................: 1 Dimensões Eixo de Baixa................: Ø230 x 370mm Roscas Sensor Temperatura..............: Não Roscas Sensor Vibração.................: Não Roscas Sensor Acelerômetro.............: Não ------------------------------ ACESSORIOS ------------------------------ Acoplamento de Alta....................: Não Acoplamento de Baixa...................: Não Sistema Contra Recuo...................: Não Braço de torque........................: Não Itens de fixação do braço de torque....: Não Lingas para braço de torque............: Não Placas de assentamento / nivelamento...: Não Itens de fixação da placa..............: Não Itens de fixação do pé.................: - Suporte para motor.....................: Não Flange do motor........................: Não Eixo tipo cardan.......................: Não Proteção para cardan...................: Não Proteção acoplamento de alta...........: Não Proteção acoplamento de baixa..........: Não Sistema de proteção principal..........: Não Sistema de proteção adicional..........: Não Bomba de lubrificação..................: Não Bomba de lubrificação (auxiliar).......: Não Bomba de lubrificação (emergência).....: Não Giro lento.............................: Não Sistema de engate \\\"Giro Lento\\\".........: Não Respiro/Filtro de ar...................: Sim (tipo FA76 40/1) Tampa de inspeção......................: Sim Sistema de lubrificação interna........: Não Interligação unidade hidráulica........: Não Unidade hidráulica.....................: Não Trocador de calor......................: Não Roda de polos..........................: Não Unidade de controle de sujidade do óleo: Não ----------------------------- DOCUMENTACAO ----------------------------- • Desenho de instalação; • Desenho de montagem; • Esquema de alinhamento; • Esquema de massas; • Esquema de óleo; • Cronograma de fabricação; • Data Book; • Manual de instruções, operação e manutenção; Nota: todos em formato eletrônico (*.PDF) em idioma Português BR. --------------------- INFORMACOES PARA INDUSTRIAL --------------------- • Inserir nas linhas indicadas da planilha anexa os roteiros, pintura e testes bem como matéria-prima e embalagem. ----------------------- INFORMACOES PARA VENDAS ----------------------- • Solicitar PIT ao departamento de qualidade; • Redutor idêntico e intercambiável ao existente O.S. 4801346; • Os itens existentes a serem utilizados devem estar em boas condições e são de responsabilidade do cliente. Medida para Jair Basso: TGM-ENGINDUSTR-ANALISAR/ESPECIFI TR Não incluso Índice RKP, Adm. Vendas, frete e comissão. **** Caso identifique alguma divergência de valores por favor nos comuniquem***SE ATENTAR NO CAMPO COMENTÁRIOS GERAIS*** Calculo de custo conforme DOC.10012448295 Medida para Roger Proenca Bento: TGM-COMERC- ANALISAR/ESPECIF REDUTO finalizada ParteObjet Causa Custos"
#     texto = unidecode(texto.lower())
#     texto = re.sub(r'[^\w\s]', ' ', texto)
#     texto = re.sub(r'\d+', ' ', texto)
#     return texto

# def gerar_stoplist(textos, freq_min=5, freq_rel=0.02):
#     total_tokens = []
#     for texto in textos:
#         texto = limpar_texto(texto)
#         doc = nlp(texto)
#         tokens = [token.lemma_ for token in doc if token.pos_ not in ['PROPN', 'NUM', 'PUNCT'] and not token.is_stop]
#         total_tokens.extend(tokens)

#     contagem = Counter(total_tokens)
#     total = sum(contagem.values())

#     stoplist = [token for token, freq in contagem.items() 
#                 if freq >= freq_min and (freq / total) >= freq_rel]
    
#     return set(stoplist)

# # Exemplo de uso
# corpus = [
#     "Aqui vai o texto 1 técnico completo...",
#     "Texto 2 com especificações, medidas, dados...",
#     "Mais um documento com redutor CSR e acessórios..."
# ]

# stopwords_geradas = gerar_stoplist(corpus)
# print("Custom Stopwords Geradas:")
# print(stopwords_geradas)

