import spacy
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
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

@st.cache_resource
def load_model(model_name):
    tokenizer =AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

@st.cache_resource
def llm_pipeline(content):
    messages = [
        {"role": "user", "content": f"{content}"},
    ]
    pipe = pipeline("text-generation", model="ContactDoctor/Bio-Medical-Llama-3-8B", use_auth_token=api_token)
    res = pipe(messages)
    return res