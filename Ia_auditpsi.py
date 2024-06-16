import streamlit as st
import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

# Configure a chave da API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Configurações do modelo
generation_config = {
  "temperature": 0.8,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

# Cria o modelo
model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction="Você é um auditor de políticas para fintechs. Seu objetivo é analisar e verificar se a fintech está com a estrutura das políticas em conformidade de acordo com os normativos do BACEN. Neste case você irá analisar uma Política de segurança cibernética tendo como base de referência o normativo 4983.",
)

# Função para ler o conteúdo dos arquivos
def ler_arquivo(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

# Função principal para a interface do Streamlit
def main():
    st.title("Auditoria de Política em Relação ao Normativo")

    st.header("Faça o upload do normativo:")
    normativo_file = st.file_uploader("Normativo", type="txt")

    st.header("Faça o upload da política de segurança cibernética:")
    politica_file = st.file_uploader("Política de Segurança Cibernética", type="txt")

    if st.button("Realizar Auditoria"):
        if normativo_file and politica_file:
            normativo = ler_arquivo(normativo_file)
            politica = ler_arquivo(politica_file)

            if normativo and politica:
                chat_session = model.start_chat(
                    history=[
                        {
                            "role": "user",
                            "parts": [
                                "Estudo o normativo 4983 do BACEN e assim que aprender me diga ok",
                                normativo,
                            ],
                        },
                        {
                            "role": "model",
                            "parts": [
                                "Ok, terminei de analisar o normativo 4983 do BACEN. Pode me apresentar a Política de Segurança Cibernética que você quer que eu analise. A partir da sua política, farei uma verificação de cada ponto em relação ao normativo.",
                            ],
                        },
                        {
                            "role": "user",
                            "parts": [
                                "Segue a política de Segurança Cibernética para ser analisada.",
                                politica,
                            ],
                        },
                    ]
                )

                response = chat_session.send_message("Por favor, faça a auditoria da política de segurança cibernética baseada no normativo fornecido.")

                st.header("Resultados da Auditoria:")
                st.write(response.text)
            else:
                st.error("Erro ao processar os arquivos. Por favor, tente novamente.")
        else:
            st.error("Por favor, faça o upload tanto do normativo quanto da política de segurança cibernética.")

if __name__ == "__main__":
    main()
