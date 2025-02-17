import streamlit as st
import pandas as pd
import torch
from API_helper_func import *
from Recommend_helper_func import *
import matplotlib.pyplot as plt
from Neo4j_helper_func import *
from secret_keys import *
from spacy_helper_func import *
from datetime import date
import google.generativeai as genai

genai.configure(api_key=gemini_api_key)
# Set page config
def set_page_layout(page_title, layout):
    st.set_page_config(page_title=page_title, layout=layout) # --> "wide", "centered"
    # setting the icon
    st.logo(image="icon.png", 
            icon_image="icon.png", size='large') 

########## User Authentication ##############
neo4j_conn = Neo4jConnection(uri="neo4j://localhost:7687", user=neo4j_user, pwd=neo4j_passwd)

session_defaults = {
    "logged_in": None,
    "selected_article": pd.DataFrame(),
    "article_df": pd.DataFrame(),
    "look": False,
    "user": None,
    "keyword": None,
    "data": None
}
for key, default in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.logged_in:
    set_page_layout("Login", "centered")
    st.title("Article Recommendation System")
    tab_register, tab_login = st.tabs(["Register", "Login"])

    with tab_register:
        st.header("Register")
        reg_firstname = st.text_input("First Name", key="reg_firstname")
        reg_lastname = st.text_input("Last Name", key="reg_lastname")
        reg_username = st.text_input("Choose a username", key="reg_username")
        reg_password = st.text_input("Choose a password", type="password", key="reg_password")
        repeat_password = st.text_input("Repeat Password", type="password", key="repeat_password")

        if st.button("Register"):
            # Validate all fields are filled
            if not all([reg_firstname, reg_lastname, reg_username, reg_password, repeat_password]):
                st.error("Please fill in all the fields.")
            elif reg_password != repeat_password:
                st.error("Passwords do not match. Please try again.")
            else:
                try:
                    user_info, user_lst = fetch_users(neo4j_conn)

                    # Check if the username already exists
                    if reg_username in user_lst:
                        # Check if the account matches the provided details
                        if (reg_firstname == user_info[reg_username]["first_name"] and 
                            reg_lastname == user_info[reg_username]["last_name"]):
                            st.error("Account already exists. Try logging in.")
                        else:
                            st.error("Username already taken. Please choose a different one.")
                    else:
                        register_user(neo4j_conn, reg_firstname, reg_lastname, reg_username, reg_password)
                        st.success("Registration successful! You can now log in.")
                except Exception as e:
                    st.error(f"Registration failed: {e}")

    with tab_login:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username and login_password:
                try:
                    status = verify_user(neo4j_conn, login_username, login_password)
                    if status:
                        st.success(f"Welcome back, {login_username}!")
                        st.session_state.logged_in = True
                        st.session_state.user = login_username
                    else:
                        st.error("Invalid username or password.")
                except Exception as e:
                    st.error(f"Login failed: {e}")
            else:
                st.error("Please fill in both fields.")

# Admin previlages               
elif st.session_state.user == 'admin':
    set_page_layout("Admin Dashboard", "centered")
    if st.button('logout'):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    st.title('Welcome back Admin!!!')
    with st.expander('Database Statistics'):
        if st.button('Get statistics'):
            stats = get_statistics(neo4j_conn)
            plot_statistics(stats)
            
    with st.expander("User management"):
        user_name = st.text_input("Username")
        if st.button('Delete user'):
            remove_user(neo4j_conn, user_name)
            st.warning(f"User {user_name} removed.")

########## App #################
else:
    set_page_layout("Article Recommendation System", "wide")
    # Multiple tabs for recommendation & NLP tasks
    tab1, tab2, tab3 = st.tabs(["Home", "NLP", "History"])

    with tab1:
        st.title('Article Recommendation System')
        with st.expander('Info'):
            st.info('''
        This project aims to develop a personalized article recommendation system tailored for biomedical
        researchers and professionals. The system will leverage the Entrez API and BioC API to retrieve
        article metadata and abstracts from PubMed and PMC, enabling users to discover relevant literature
        efficiently. Using advanced natural language processing (NLP) techniques and similarity-based
        matching, the system recommends articles based on content relevance.
        ''')

        # API query parameters
        with st.sidebar:
            # logout button --> resets everything
            if st.button('logout'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

            st.write('Select parameters')
            key_word = st.text_input('Enter the search keyword')
            mindate = st.date_input('Enter starting date', value=date(2020, 12, 7))
            maxdate = st.date_input('Enter ending date', value=date(2024, 12, 7))
            if mindate > maxdate:
                st.error("Starting date must be earlier than the ending date!")
            retmode = st.radio('Pick one', ['json', 'xml'])
            retmax = st.selectbox('Select:', [10, 20, 50, 100])
            status = st.button('Proceed')

            if st.button("New Search"):
                # Clear relevant session state keys
                keys_to_clear = ["selected_article", "recommended_articles", "look", "keys", "article_df", "data"]
                for key in keys_to_clear:
                    if key in st.session_state:
                        st.session_state[key] = None
                reset_defaults = {
                    "article_df": pd.DataFrame(),
                    "selected_article": pd.DataFrame(),
                    "recommended_articles": pd.DataFrame(),
                    "look": False,
                    "keys": None
                }
                for key, default in reset_defaults.items():
                    st.session_state[key] = default
                    

        # Storing the keyword in Session
        st.session_state.keyword = key_word

        if status:
            mindate = str(mindate.strftime("%d/%m/%Y"))
            maxdate = str(maxdate.strftime("%d/%m/%Y"))

            params = {
                'keyword': f'{key_word} AND free full text', 
                'mindate': mindate, 
                'maxdate': maxdate, 
                'retmode': retmode, 
                'retmax': retmax
            }

            if retmode == "json":
                # API calls
                with st.spinner("Fetching data..."):
                    data, article_ids = fetch_article_id(**params)
                    article_df = run_script(article_ids)

                # Save the DataFrame to session state
                st.session_state.article_df = article_df
                st.session_state.data = data

            else:
                st.warning("Work in progress for XML format...")

        article_df = st.session_state.article_df

        # Visualizing Data Expander
        with st.expander("Data"):
            if st.session_state["article_df"].empty:
                st.warning("No data available. Please search to load data.")
            else:
                st.dataframe(st.session_state["article_df"])

        # Information about total hits and data retrieved
        with st.expander('**Visualisation**'):
            col1, col2 = st.columns(2)
            try:
                if 'data' in st.session_state:
                    data = st.session_state['data'] 
                    total_results = int(data['esearchresult']['count'])
                    returned_results = int(data['esearchresult']['retmax'])

                    # API Metrics
                    with col2:
                        st.metric(label="Total Results", value=total_results)
                        st.metric(label="Returned Results", value=returned_results)

                    # Bar graph
                    with col1:
                        st.subheader("Total vs Returned Results")
                        fig, ax = plt.subplots(figsize=(4, 5))
                        ax.bar(["Total Results", "Returned Results"], [total_results, returned_results], color=["blue", "orange"])
                        ax.set_ylabel("Count")
                        ax.set_title("Total vs Returned Results")
                        st.pyplot(fig)

            except Exception as e:
                st.error(f"Error generating visualization: No data.")

        # Initializing the button 'look'
        if "look" not in st.session_state:
            st.session_state.look = False

        # Abstract Viewer Expander
        with st.expander("**Section**"):
            section = st.selectbox(
            "Pick a section:", ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion'], 
            index=0,
            key="section_selectbox")

            if not article_df.empty:
                # Use session state to retain the slider value
                if "slider_val" not in st.session_state:
                    st.session_state.slider_val = 1 

                # Slider for selecting an abstract
                val = st.slider(
                    "Select Article Index", 
                    min_value=1, 
                    max_value=min(retmax, len(article_df)), 
                    value=st.session_state.slider_val,
                    step=1
                )

                # Fetch the selected article details
                if "selected_article" not in st.session_state:
                    st.session_state["selected_article"] = pd.DataFrame()

                if not article_df.empty:
                    selected_article = article_df.iloc[val - 1]
                    st.write(f"**Title:** {selected_article['Title']}")
                    st.write(f"**PMCID:** {selected_article['pmcid']}")
                    st.text_area(f"**{section}:**", selected_article[section], height=300, key='articles_to_select')
                    
                    if st.button('Look for similar articles', key=f'similar_articles_{val}'):
                        st.session_state["look"] = True
                        st.session_state["selected_article"] = selected_article

                        # Add to Neo4j
                        user = st.session_state.get("user", "")
                        keyword = st.session_state.get("keyword", "")
                        add_selected(neo4j_conn, selected_article, user, keyword)
                else:
                    st.warning("No articles to display.")

        selected_article = st.session_state.selected_article

        # Recommend articles based on cosine similarity
        if st.session_state.look:
            with st.spinner("Looking for similar articles..."):
                with st.expander("**Recommended articles**"):
                    article = selected_article
                    article = article['Abstract']
                    all_abstracts = article_df['Abstract'].to_list()

                    # Vectorization and cosine similarity
                    similarity = get_similar_articles(article, all_abstracts, method='bert')
                    recommend = get_recommendation(similarity, article_df)

                    # Adding recommended to database
                    selected = st.session_state.selected_article
                    user = st.session_state.user
                    add_recommended(neo4j_conn, recommend, selected, user)

                    # Recommend articles in different tabs
                    rec1, rec2, rec3, rec4, rec5 = st.tabs(['Article 1', 'Article 2', 'Article 3', 'Article 4', 'Article 5'])
                    # Adding keys to session state
                    if 'keys' not in st.session_state:
                        st.session_state.keys = None
                    keys = list(recommend.keys())
                    st.session_state.keys = keys
                    section = st.selectbox(
                            "Pick a section:", ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion'], 
                            index=0,
                            key="recommendation_section_selectbox")
                    
                    ################# Recommended Article tabs ###############
                    rec_lst = [rec1, rec2, rec3, rec4, rec5]
                    rec_df_lst = []
                    # Articles
                    for idx, rec in enumerate(rec_lst):
                        info = display_recommended(article_df, recommend, keys[idx+1], section, rec)
                        rec_df_lst.append(info)


    with tab2:
        nlp, chat = st.columns(2)
        with nlp:
            st.title("NLP tasks")
            with st.expander('Info'):
                st.info("""
                This is a workspace to perform various basic NLP tasks. The following tasks can be performed using **spaCy base models**:
                
                - **Tokenization**: Breaks a text into smaller units such as words or sentences.
                - **Named Entity Recognition (NER)**: Identifies and classifies entities (e.g., names, dates, locations) in the text.
                - **Part-of-Speech (POS) Tagging**: Assigns grammatical labels (e.g., noun, verb) to words in a text.
                - **Dependency Parsing**: Analyzes the grammatical structure of a sentence by identifying relationships between words.
                - **Sentence Boundary Detection (SBD)**: Automatically detects sentence boundaries in a given text.
                - **Lemmatization**: Converts words to their base or dictionary form (e.g., "running" → "run").
                
                These tasks leverage the power of spaCy’s efficient and pretrained pipelines, which are optimized for multiple languages.

                Explore these tasks and more!
                """)

            with st.expander('Article'):
                section = st.selectbox("Pick a section:", ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion'], 
                    index=0,key="section_selectbox_tokens")
                
                text = ""
                if "selected_article" in st.session_state and not st.session_state.selected_article.empty:
                    selected = st.session_state.selected_article
                    st.write(f"**Title:** {selected['Title']}")
                    st.text_area(f"**{section}:**", selected.get(section, ""), height=150, key='nlp_section')
                    text = selected.get(section, "")
                else:
                    st.warning("No article selected. Please select an article to analyze.")
            
            text_area = st.text_area("Enter custom text for NLP tasks")

            ################ NLP TASKS ######################
            with st.expander('Tasks'):
                task = st.selectbox("Pick a section:", ['None', 'Tokenize', 'Sentencize', 'NER', 'Lemmatize', 'POS tag'], 
                    index=0,key="task_selectbox")
            
                text_to_process = text_area if text_area else text

                if text_to_process.strip():
                    # Perform NLP tasks based on the selected task
                    if task == 'Tokenize':
                        tokens = get_tokenized_text(text_to_process)
                        st.write("### Tokens")
                        st.markdown(" | ".join(tokens))

                    elif task == 'Sentencize':
                        sentences = get_sentences(text_to_process)
                        st.write("### Sentences")
                        for i, sentence in enumerate(sentences, 1):
                            st.markdown(f"**Sentence {i}:** {sentence}")

                    elif task == 'NER':
                        entities = get_ner(text_to_process)
                        st.write("### Named Entities")
                        if entities:
                            entity_df = pd.DataFrame(entities, columns=["Entity", "Label"])
                            st.table(entity_df)

                    elif task == 'Lemmatize':
                        lemmas = lemmatize_text(text_to_process)
                        st.write("### Lemmas")
                        if lemmas:
                            lemma_df = pd.DataFrame(lemmas, columns=["Original form", "Lemma form"])
                            st.table(lemma_df)

                    elif task == 'POS tag':
                        pos = get_pos_tags(text_to_process)
                        st.write("### POS tags")
                        if pos:
                            pos_df = pd.DataFrame(pos, columns=["Text", "POS", "Tag"])
                            st.table(pos_df)
                else:
                    st.warning("Please enter text or select a section to process.")
        with chat:
            # ChatBot for assistance
            st.title("Chat with AI 🤖 assistant")
            default_question = "What is Natural Language Processing?"
            user_input = st.text_input("Ask your questions..", value=default_question, key="gen_chat_input")
            if st.button("Send", key='send_chat'):
                if user_input.strip():
                    # Generate AI response
                    bot_response = genai_response(user_input.strip())
                    st.write(bot_response)

    with tab3:
        # Shows last 5 selected articles
        user = st.session_state.user
        history = fetch_history(neo4j_conn, user)
        history = pd.DataFrame(history, columns=['Search term', 'pmcid', 'title'])
        st.dataframe(history)

