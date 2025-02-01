import spacy
import streamlit as st
import google.generativeai as genai
from secret_keys import *

nlp = spacy.load("en_core_web_sm")

############## NLP functions #################
@st.cache_data
def get_tokenized_text(text):
    doc = nlp(text)
    tokens = [token.text for token in doc]
    return tokens

@st.cache_data
def get_ner(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

@st.cache_data
def get_pos_tags(text):
    doc = nlp(text)
    pos_tags = [(token.text, token.pos_, token.tag_) for token in doc]
    return pos_tags

@st.cache_data
def lemmatize_text(text):
    doc = nlp(text)
    lemmas = [(token.text, token.lemma_) for token in doc]
    return lemmas

@st.cache_data
def get_sentences(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return sentences

@st.cache_resources
def genai_response(question):
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 150,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(model_name='gemini-pro', generation_config=generation_config)
    prompt = f"""
    Hey, you're a personal assistant and an expert in Natural Language Processing and Biomedical domain.
    Explain the following question in about 50 to 100 words:
    {question}
    """  
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"