import streamlit as st
from openai import OpenAI
import os

# Configuração da página do site
st.set_page_config(page_title="Tradutor de Vídeo por IA", page_icon="🎬", layout="centered")

st.title("🎬 Tradutor e Dublador de Vídeo por IA")
st.write("Envie seu arquivo de áudio ou vídeo para transcrever e traduzir com Inteligência Artificial!")

# Campo para o usuário colocar a chave da API
api_key = st.text_input("Cole sua OpenAI API Key aqui:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # Upload do arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo de áudio/vídeo (MP3, MP4, WAV, M4A)", type=["mp3", "mp4", "wav", "m4a"])

    # Seleção de idioma
    target_language = st.selectbox(
        "Para qual idioma deseja traduzir?",
        ["Português", "Inglês", "Espanhol", "Francês", "Alemão", "Italiano"]
    )

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("🚀 Iniciar Tradução"):
            with st.spinner("Processando... Transcrevendo e traduzindo o conteúdo..."):
                try:
                    # Salvando arquivo temporário
                    temp_filename = f"temp_{uploaded_file.name}"
                    with open(temp_filename, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # 1. Transcrição com Whisper
                    with open(temp_filename, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file
                        )

                    text_original = transcript.text
                    st.subheader("📝 Transcrição Original:")
                    st.write(text_original)

                    # 2. Tradução com GPT-4o
                    prompt = f"Traduza o texto a seguir com precisão para o idioma {target_language}:\n\n{text_original}"
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    translated_text = response.choices[0].message.content
                    st.subheader("🌐 Texto Traduzido:")
                    st.write(translated_text)

                    # 3. Geração de Áudio Traduzido (Text-to-Speech)
                    st.subheader("🔊 Áudio Dublado por IA:")
                    speech_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=translated_text
                    )
                    
                    audio_output_path = "audio_traduzido.mp3"
                    speech_response.stream_to_file(audio_output_path)
                    
                    # Exibir player de áudio e botão para download
                    st.audio(audio_output_path)
                    with open(audio_output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Baixar Áudio Dublado",
                            data=file,
                            file_name="dublagem_traduzida.mp3",
                            mime="audio/mp3"
                        )

                    # Limpar arquivo temporário
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)

                except Exception as e:
                    st.error(f"Ocorreu um erro durante o processamento: {e}")
else:
    st.info("Por favor, insira sua OpenAI API Key acima para ativar a plataforma.")
