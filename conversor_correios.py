import streamlit as st
import xml.etree.ElementTree as ET
import json
import pandas as pd
import re
from urllib.parse import quote

# Configurações de Caixas
CAIXAS_PADRAO = {
    "Baianinha": {"p": "4000", "a": "44", "l": "25", "c": "44"},
    "Casadeira": {"p": "6000", "a": "44", "l": "25", "c": "55"},
    "Trinca": {"p": "6000", "a": "50", "l": "30", "c": "50"},
    "Piracicaba": {"p": "8000", "a": "60", "l": "55", "c": "30"},
    "2Baianinha": {"p": "8000", "a": "44", "l": "44", "c": "44"},
    "2Casadeiras": {"p": "12000", "a": "44", "l": "44", "c": "55"},
    "3Baianinhas": {"p": "12000", "a": "44", "l": "44", "c": "60"},
    "Personalizado...": {"p": "100", "a": "15", "l": "15", "c": "20"}
}

def tratar_telefone_unico(texto_fone):
    if not texto_fone: return "", ""
    numeros = re.sub(r'\D', '', str(texto_fone))
    if len(numeros) >= 10:
        return numeros[:2], numeros[2:]
    return "", numeros

def extrair_dados_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
        inf = root.find('.//ns:infNFe', ns)
        if inf is None: return None

        nNF = inf.find('.//ns:ide/ns:nNF', ns).text
        chave = inf.attrib['Id'].replace('NFe', '')
        
        # Remetente
        emit = inf.find('.//ns:emit', ns)
        nome_fantasia = emit.find('ns:xFant', ns).text if emit.find('ns:xFant', ns) is not None else emit.find('ns:xNome', ns).text
        fone_emit = emit.find('.//ns:fone', ns).text if emit.find('.//ns:fone', ns) is not None else ""
        ddd_e, num_e = tratar_telefone_unico(fone_emit)

        # Destinatário
        dest = inf.find('.//ns:dest', ns)
        doc_dest = dest.find('ns:CPF', ns)
        if doc_dest is None: doc_dest = dest.find('ns:CNPJ', ns)
        fone_dest = dest.find('.//ns:fone', ns).text if dest.find('.//ns:fone', ns) is not None else ""

        itens = []
        total_valor = 0
        for det in inf.findall('ns:det', ns):
            prod = det.find('ns:prod', ns)
            v = float(prod.find('ns:vProd', ns).text)
            total_valor += v
            itens.append({"conteudo": prod.find('ns:xProd', ns).text, "quantidade": int(float(prod.find('ns:qCom', ns).text)), "valor": v})

        return {
            "nNF": nNF, "chave": chave, "loja": nome_fantasia,
            "remetente": {"nome": emit.find('ns:xNome', ns).text, "cpfCnpj": emit.find('ns:CNPJ', ns).text, "ddd": ddd_e, "celular": num_e, "end": {"cep": emit.find('.//ns:CEP', ns).text, "log": emit.find('.//ns:xLgr', ns).text, "nro": emit.find('.//ns:nro', ns).text, "bairro": emit.find('.//ns:xBairro', ns).text, "cid": emit.find('.//ns:xMun', ns).text, "uf": emit.find('.//ns:UF', ns).text}},
            "destinatario": {"nome": dest.find('ns:xNome', ns).text, "cpfCnpj": doc_dest.text if doc_dest is not None else "", "fone_completo": fone_dest, "email": dest.find('ns:email', ns).text if dest.find('ns:email', ns) is not None else "", "end": {"cep": dest.find('.//ns:CEP', ns).text, "log": dest.find('.//ns:xLgr', ns).text, "nro": dest.find('.//ns:nro', ns).text, "comp": dest.find('.//ns:xCpl', ns).text if dest.find('.//ns:xCpl', ns) is not None else "", "bairro": dest.find('.//ns:xBairro', ns).text, "cid": dest.find('.//ns:xMun', ns).text, "uf": dest.find('.//ns:UF', ns).text}},
            "itens": itens, "total": total_valor
        }
    except: return None

# --- UI ---
st.set_page_config(page_title="Bruno do Preá - Postagem", layout="wide", page_icon="📦")
st.title("📦 Sistema de Postagem - Bruno do Preá Rações")

# Inicializa estado para armazenar dados processados para o WhatsApp
if 'dados_whatsapp' not in st.session_state:
    st.session_state.dados_whatsapp = []

uploaded_files = st.file_uploader("Arraste os XMLs aqui", type="xml", accept_multiple_files=True)

if uploaded_files:
    registros_finais = []
    temp_whatsapp = []
    
    for idx, file in enumerate(uploaded_files):
        dados = extrair_dados_xml(file)
        if not dados: continue

        with st.expander(f"📝 Nota {dados['nNF']} - {dados['destinatario']['nome']}"):
            c1, c2, c3 = st.columns([1.5, 1.2, 1.3])
            with c1:
                st.dataframe(pd.DataFrame(dados['itens']), hide_index=True)
            with c2:
                tipo_caixa = st.selectbox("Caixa", list(CAIXAS_PADRAO.keys()), key=f"b_{idx}")
                medidas = CAIXAS_PADRAO[tipo_caixa]
                p = st.text_input("Peso (g)", medidas['p'], key=f"p_{idx}")
                alt = st.text_input("Altura", medidas['a'], key=f"a_{idx}")
                larg = st.text_input("Largura", medidas['l'], key=f"l_{idx}")
                comp = st.text_input("Comprimento", medidas['c'], key=f"c_{idx}")
            with c3:
                fone_manual = st.text_input("Telefone (DDD + Número)", dados['destinatario']['fone_completo'], key=f"t_{idx}")
                ddd_f, cel_f = tratar_telefone_unico(fone_manual)
                st.caption(f"Identificado: ({ddd_f}) {cel_f}")

            # Montagem JSON
            obj = {
                "sequencial": str(idx + 1),
                "codigoServico": "03220",
                "pesoInformado": str(p),
                "codigoFormatoObjetoInformado": "2",
                "alturaInformada": str(alt), "larguraInformada": str(larg), "comprimentoInformado": str(comp),
                "diametroInformado": "", "cienteObjetoNaoProibido": 1,
                "numeroNotaFiscal": dados['nNF'], "chaveNFe": dados['chave'],
                "itensDeclaracaoConteudo": dados['itens'],
                "destinatario": {"cpfCnpj": dados['destinatario']['cpfCnpj'], "nome": dados['destinatario']['nome'], "dddCelular": ddd_f, "celular": cel_f, "email": dados['destinatario']['email'], "endereco": {"cep": dados['destinatario']['end']['cep'], "logradouro": dados['destinatario']['end']['log'], "numero": dados['destinatario']['end']['nro'], "complemento": dados['destinatario']['end']['comp'], "bairro": dados['destinatario']['end']['bairro'], "cidade": dados['destinatario']['end']['cid'], "uf": dados['destinatario']['end']['uf']}},
                "remetente": {"cpfCnpj": dados['remetente']['cpfCnpj'], "nome": dados['remetente']['nome'], "dddCelular": dados['remetente']['ddd'], "celular": dados['remetente']['celular'], "email": "", "endereco": {"cep": dados['remetente']['end']['cep'], "logradouro": dados['remetente']['end']['log'], "numero": dados['remetente']['end']['nro'], "complemento": "", "bairro": dados['remetente']['end']['bairro'], "cidade": dados['remetente']['end']['cid'], "uf": dados['remetente']['end']['uf']}},
                "listaServicoAdicional": [{"codigoServicoAdicional": "019", "valorDeclarado": dados['total']}]
            }
            registros_finais.append(obj)
            # Guarda dados para o WhatsApp
            temp_whatsapp.append({"nome": dados['destinatario']['nome'], "telefone": f"55{ddd_f}{cel_f}", "loja": dados['loja']})

    if st.button("🚀 1. GERAR JSON PARA CORREIOS", type="primary", use_container_width=True):
        st.session_state.dados_whatsapp = temp_whatsapp # Salva para a etapa do Zap
        json_str = json.dumps(registros_finais, indent=4, ensure_ascii=False)
        st.download_button("✅ Baixar Arquivo", json_str, "correios.json", "application/json", use_container_width=True)

# --- ETAPA WHATSAPP ---
# --- ETAPA WHATSAPP (Substitua a partir do divider) ---
if st.session_state.dados_whatsapp:
    st.divider()
    st.subheader("📲 2. Enviar Rastreio e Oferta via WhatsApp")
    st.info("O link abaixo abrirá o chat. Se preferir, use a caixa de texto para copiar manualmente.")
    
    for i, cliente in enumerate(st.session_state.dados_whatsapp):
        # Criamos um container visual para cada cliente
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 1.2])
            
            with c1:
                st.write(f"👤 **{cliente['nome']}**")
                st.caption(f"📞 {cliente['telefone']}")
            
            with c2:
                # Campo para o código de rastreio
                rastreio = st.text_input(f"Cód. Rastreio", key=f"ras_{i}", placeholder="Ex: AA123456789BR").upper().strip()
            
            with c3:
                if rastreio:
                    # Link de rastreio direto
                    link_rastreio_direto = f"https://rastreamento.correios.com.br/app/index.php?objeto={rastreio}"
                    
                    # Mensagem formatada
                    msg = (
                        f"Olá *{cliente['nome']}*, aqui é do *{cliente['loja']}*. 🐾\n\n"
                        f"Segue o código de rastreio do seu pedido: *{rastreio}*\n"
                        f"Você pode acompanhar clicando aqui: {link_rastreio_direto}\n\n"
                        f"Também preparamos um tutorial para te ajudar: https://www.youtube.com/watch?v=wrQ0RIqyEFc \n\num dos nossos atendentes vai entrar em contato com você para, "
                        f"caso queira comprar algo a mais, aproveitar o frete grátis! 📦\n\n"
                        f"Obrigado pela preferência!"
                    )
                    
                    # Link para abrir o WhatsApp
                    link_wa = f"https://wa.me/{cliente['telefone']}?text={quote(msg)}"
                    st.link_button("💬 Abrir no WhatsApp", link_wa, use_container_width=True, type="primary")
                else:
                    st.button("⚠️ Digite o rastreio acima", disabled=True, key=f"dis_{i}", use_container_width=True)

            # Se o rastreio foi digitado, mostramos a caixa de cópia abaixo dos botões
            if rastreio:
                with st.expander("📋 Ver/Copiar texto da mensagem"):
                    # st.code fornece o botão de "Copiar" automático no canto
                    st.code(msg, language=None)