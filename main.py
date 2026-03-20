import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

st.set_page_config(page_title="Extrator de EAN", layout="centered")
st.title("📦 Extrator de XML para Excel")
st.write("Arraste seus arquivos XML (NFe ou NFSe) abaixo.")

# Interface de Drop
uploaded_files = st.file_uploader("Escolha os arquivos XML", type="xml", accept_multiple_files=True)

if uploaded_files:
    dados = []
    ns_nfe = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    ns_nfse = {'nfse': 'http://www.sped.fazenda.gov.br/nfse'}

    for file in uploaded_files:
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            tag_root = str(root.tag)

            if "portalfiscal" in tag_root:
                for det in root.findall('.//nfe:det', ns_nfe):
                    prod = det.find('nfe:prod', ns_nfe)
                    if prod is not None:
                        dados.append({
                            'Descricao': prod.findtext('nfe:xProd', '', ns_nfe),
                            'EAN': prod.findtext('nfe:cEAN', '', ns_nfe)
                        })
            elif "sped.fazenda" in tag_root:
                serv = root.find('.//nfse:serv', ns_nfse)
                if serv is not None:
                    dados.append({
                        'Descricao': serv.findtext('.//nfse:xDescServ', '', ns_nfse),
                        'EAN': 'N/A (SERVIÇO)'
                    })
        except Exception as e:
            st.error(f"Erro no arquivo {file.name}: {e}")

    if dados:
        df = pd.DataFrame(dados)
        st.success(f"{len(dados)} itens extraídos com sucesso!")
        st.dataframe(df) # Mostra uma prévia na tela

        # Gerar Excel na memória para download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        
        st.download_button(
            label="📥 Baixar Excel Pronto",
            data=output.getvalue(),
            file_name="ean_extraidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        