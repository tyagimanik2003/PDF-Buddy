import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
from transformers import pipeline
import base64
from st_on_hover_tabs import on_hover_tabs
import streamlit_authenticator as stauth 
from gtts import gTTS
from translate import Translator as TranslateTranslator

credentials = {
    "usernames":{
        "Manik":{
            "name":"Manik Tyagi",
            "password":"$2b$12$nCU6X0wZAZulRMgIiohEteC8yel6TwLlRTJaz5fCNJep.ulAZ.xZi"
            },        
        }
    }

st.image("logo.png")
authenticator = stauth.Authenticate(credentials, "app_home", "auth", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status == True:
    # st.write("Hello")
    # authenticator.logout("logout","main")
    @st.cache_data
    def add_bg_from_local(image_file):
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-size: cover;
            

        }}
        </style>
        """,
        unsafe_allow_html=True
        )

    def ocr_pdf(file):
        pages = convert_from_bytes(file.read(), 500, poppler_path=r"C:\Program Files\poppler-23.07.0\Library\bin")
        text = ""
        for page in pages:
            text_data = pytesseract.image_to_string(page)
            text += text_data
        return text


    add_bg_from_local('F:\OCR app\image.png')
    st.markdown('<style>' + open('style.css').read() + '</style>', unsafe_allow_html=True)


    with st.sidebar:
        tabs = on_hover_tabs(tabName=['Home','Chatbot'], 
                            iconName=['info','history_edu'], default_choice=0)
        authenticator.logout("logout","main")
    if tabs=="Home":
        st.markdown("# Welcome to PDF Buddy!")
        st.markdown("This project allows users to upload a PDF document and ask questions about its content. It combines OCR (Optical Character Recognition) technology and a question-answering model to provide answers to user questions based on the text extracted from the uploaded PDF.")
        st.subheader("About")
        st.markdown("This Streamlit project is designed for PDF Document QA. It leverages OCR technology and a question-answering model to provide answers to questions about the content of uploaded PDF documents.")

        st.subheader("Usage Guide")
        st.markdown("1. Navigate to the 'Chatbot' tab.")
        st.markdown("2. Upload a PDF document that you want to ask questions about.")
        st.markdown("3. Select the language in which you want the answer.")
        st.markdown("4. Type your question in the input field.")
        st.markdown("5. Click the 'Get Answer' button.")
        st.markdown("6. The answer will be displayed, translated (if selected), and available in audio format.")




    elif tabs=="Chatbot":
        uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

        if uploaded_file is not None:

            
            model_checkpoint = "consciousAI/question-answering-roberta-base-s-v2"
            question_answerer = pipeline("question-answering", model=model_checkpoint)

            languages = {
                "English": "en",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                "Italian": "it",
            }
            
            selected_language = st.selectbox("In which language do you want your answer:", list(languages.keys()), index=0)

            user_question = st.text_input("Ask a question about the document:")
            if st.button("Get Answer"):

                text = ocr_pdf(uploaded_file)
                result = question_answerer(question=user_question, context=text)

                st.write("Answer:", result["answer"])
                answer = result["answer"]


                language_code = languages[selected_language]
                translator = TranslateTranslator(to_lang=language_code)
                answer = translator.translate(answer)
                st.write(f"Answer({selected_language}): ",answer)


                tts = gTTS(text=answer, lang=language_code)

                output_file = "output.mp3"  
                tts.save("F:\Chatbot_Streamlit\output.mp3")
                st.audio("F:\Chatbot_Streamlit\output.mp3", start_time=0)