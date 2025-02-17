# **Article Recommendation System**
## 📖 Overview:
This project aims to develop a personalized article recommendation system tailored for biomedical researchers and professionals. The system will leverage the [Entrez API](https://biopython.org/docs/1.75/api/Bio.Entrez.html) and [BioC API](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/) to retrieve full text article from PubMed and PMC, enabling users to discover relevant literature efficiently. Using advanced natural language processing (NLP) techniques and similarity-based matching, the system recommends articles based on content relevance. The user-friendly [Streamlit](https://docs.streamlit.io/) interface allows for dynamic filtering, keyword search, and article exploration, while all user and article metadata are stored in a robust [Neo4j](https://neo4j.com/docs/) graph database for efficient authentication and querying.
## ⚙️ Functionalities
1. **Data Source and Retrieval**
The primary data sources are: 
+ Entrez API: Fetch metadata (PMIDs and PMCIDs) from PubMed and PMC using keyword-based or structured queries. 
+ BioC API: Retrieve full-text articles based on the PMCIDs.  
2. **Data Storage and Handling**
The system employs a Neo4j graph database to efficiently store and manage user interactions, article metadata, and relationships. 
+ Nodes: Users (with properties like username and password). Articles (storing metadata such as title, abstract). 
+ Relationships: SELECTED and RECOMMENDED relationships between user and articles.
3. **Data Processing**
+ NLP tasks: [spaCy](https://spacy.io/api/doc/) for NLP related tasks.
+ Embeddings: Compute contextual embeddings of article abstracts using BERT [transformer](https://huggingface.co/docs/transformers/index) model for similarity calculations. 
3. **Interface**
The front end will be a sleek, intuitive Streamlit application that allows users to:
+ Register and Log In: User credentials stored securely in Neo4j.
+ Filter and Search: Keyword-based article search and filtering by publication year.
+ Recommendation Dashboard: Display of recommended articles based on user selection.
4. **Statistical Analysis**
The system uses statistical methods to drive recommendations: 
+ Cosine Similarity: Measure similarity between article abstracts using their BERT contextual embeddings.
5. **Visualizations**
+ Article Availability: Bar charts showing the number of hits based on the user query.
+ Databse Visualizations: Overall statistics of the database.
## 📌 **NLP toolkit**
A dedicated tab for various NLP tasks, including:
+ Named Entity Recognition (NER): Identify key entities.
+ Tokenization: Split the text into meaningful units.
+ Lemmatization: Reduce the words to their base form.
+ Part-Of-Speech (POS) Tagging: Understand the gramatical structure of text.
## 💬 **Chatbot Intergration**
+ Gemini-Pro Chatbot for interactive queries.
+  Get insights on articles, NLP concepts, and more.
## 📦 Tools and Libraries
| Tasks             |  Tools                 |
|-------------------|------------------------|
| APIs              |  Entrez API, BioC API  |
| Databases         |  Neo4j                 |
| NLP               |  spaCy                 |
| Embeddings        |  Transformer           |
| Cosine Similarity |  Scikit-learn          |
| Web Development   |  Streamlit             |
| Visualization     |  Matplotlib, Plotly    |
## Installation and Usage
Install required packages:
```bash
pip install -r requirements.txt
```
To run the streamlit app:
```python
streamlit run Streamlit_RecomApp.py
```
## 📅 Timeline
![](https://github.com/GokulPrakashK98/DataScienceProject/blob/main/Timeline.jpg)
## 🤝 Group Details
* Group Name: Core-Code Crew
* Group Code: G23
* Tutor Responsible: Frederik, Hennecke
* Group team leader: Sreelakshmi, Ramesh
* Group Members: Kolakkattil, Gokul Prakash & Ramesh, Sreelakshmi

Gokul managed the NLP tasks and Neo4j database administration, while Sreelakshmi developed the API functions to gather data based on user queries and took care of the entire documentation. Both shared the responsibility for the Streamlit interface.
## 📢 Acknowledgement
We would like to express our gratitude to the following individuals and organizations for their valuable contributions and support throughout the development of this project:
+ Prof. Bela Gipp & Gipp Lab: We are deeply thankful for the opportunity to participate in the lecture and group project under your guidance and mentorship.
+ Frederik Hennecke: Our tutor, whose insightful feedback and guidance were instrumental in shaping our project and enhancing our understanding.
+ Terry Lima Ruas: Our lecturer whose expertise and encouragement significantly contributed to the success and growth of our project.
+ Corey Schafer & SpaCy Explosion: A sincere thanks for the insightful tutorials and educational content on YouTube, which greatly enhanced our understanding of key concepts.
We are grateful for the support and resources provided by these individuals and organizations, which were instrumental in the completion of this project.
