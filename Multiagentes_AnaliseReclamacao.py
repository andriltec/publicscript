import streamlit as st
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Carregar as variáveis de ambiente
load_dotenv()

# Configurar a chave da API do Google
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("Chave da API não configurada. Defina a variável de ambiente 'GOOGLE_API_KEY'.")
    st.stop()

# Configuração do modelo Gemini
chat_model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

class Agent:
    def __init__(self, model, role, tasks, backhistory):
        self.model = model
        self.role = role
        self.tasks = tasks
        self.backhistory = backhistory

    def run(self, prompt):
        results = []
        for task in self.tasks:
            full_prompt = f"{self.backhistory} {task} {prompt}"
            response = self.model.invoke(full_prompt)
            results.append(response.content)
        return results

# Definição dos agentes
analista = Agent(
    model=chat_model,
    role="Analista",
    tasks=[
        "Listar tópicos principais da reclamação:",
        "Analisar sentimentos da reclamação:",
        "Avaliar eficácia do feedback da empresa:",
        "Máximo de 300 tokens"
    ],
    backhistory="Agentes especializados em análise de texto e feedbacks, formados com vastos dados de interações de serviço ao cliente."
)

supervisor = Agent(
    model=chat_model,
    role="Supervisor",
    tasks=["Avaliar o lote de reclamações analisadas e sugerir melhorias gerais:"],
    backhistory="Supervisor com alta capacidade de síntese e avaliação global, focado em melhorar a qualidade geral das respostas."
)

# Interface do Streamlit
st.title("Upload e Análise de Reclamações com Gemini")
uploaded_file = st.file_uploader("Carregue o arquivo JSON de reclamações aqui", type=['json'])

if uploaded_file is not None:
    data = json.load(uploaded_file)
    reclamacoes = data['reclamacoes']

    if st.button('Iniciar Trabalho'):
        with st.spinner("Processando..."):
            all_feedbacks = []

            for reclamacao in reclamacoes:
                id_reclamacao = reclamacao['id']
                mensagem = reclamacao['mensagem']
                resposta = reclamacao.get('resposta', {}).get('mensagem', 'Sem resposta')

                # Executar as análises com sequência determinada
                results = analista.run(mensagem + " " + resposta)
                all_feedbacks.extend(results)
                
                with st.expander(f"ID {id_reclamacao} - Análise Detalhada"):
                    st.write("Tópicos Principais:", results[0])
                    st.write("Análise de Sentimentos:", results[1])
                    st.write("Avaliação de Eficácia:", results[2])
                    st.write("Sugestões de Melhorias:", results[3])

            # Avaliação global pelo supervisor
            general_feedback = supervisor.run(" ".join(all_feedbacks))

            st.success("Análise concluída!")
            st.subheader("Avaliação Geral pelo Supervisor:")
            st.write(general_feedback[0])
