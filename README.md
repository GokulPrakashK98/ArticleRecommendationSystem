# **Article Recommendation System**
## Overview:
This project aims to develop a personalized article recommendation system tailored for biomedical researchers and professionals. The system will leverage the [Entrez API](https://biopython.org/docs/1.75/api/Bio.Entrez.html) and [BioC API](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/) to retrieve article metadata and abstracts from PubMed and PMC, enabling users to discover relevant literature efficiently. Using advanced natural language processing (NLP) techniques and similarity-based matching, the system recommends articles based on content relevance. The user-friendly [Streamlit](https://docs.streamlit.io/) interface allows for dynamic filtering, keyword search, and article exploration, while all user and article metadata are stored in a robust [Neo4j](https://neo4j.com/docs/) graph database for efficient authentication and querying.
## Functionalities
1. **Data Source and Retrieval**
The primary data sources are: 
+ *Entrez API*: Fetch metadata (e.g., article titles, abstracts, DOI, publication date) from PubMed and PMC using keyword-based or structured queries. 
+ *BioC API*: Retrieve full-text data for deeper analysis from PMC articles.  
2. **Data Storage and Handling**
The system employs a Neo4j graph database to efficiently store and manage user interactions, article metadata, and relationships. 
+ *Nodes*: Users (with properties like username and password). Articles (storing metadata such as title, abstract). 
+ *Relationships*: Semantic links between similar articles (SIMILAR_TO) based on cosine similarity. 
+ *Preprocessing*: [spaCy](https://spacy.io/api/doc/) for cleaning and tokenizing text data (e.g., abstracts).
+ *Embeddings*: Compute contextual embeddings of article abstracts using BERT [transformer](https://huggingface.co/docs/transformers/index) model for similarity calculations. 
3. **Interface**
The front end will be a sleek, intuitive Streamlit application that allows users to:
+ *Register and Log In*: User credentials stored securely in Neo4j.
+ *Filter and Search*: Keyword-based article search and filtering by publication year.
+ *Recommendation Dashboard*: Display of recommended articles based on user selection.
4. **Statistical Analysis**
The system uses statistical methods to drive recommendations: 
+ *Cosine Similarity*: Measure similarity between article abstracts using their BERT contextual embeddings.
5. **Visualizations**
+ *Article Availability*: Bar charts showing the number of hits based on the user query.
+ *Neo4j Graph Visualizations*: Showcase relationships between article.
## Timeline
![](https://github.com/GokulPrakashK98/DataScienceProject/blob/main/Timeline.png)
## Tools and Libraries
| Tasks             |  Tools                 |
|-------------------|------------------------|
| APIs              |  Entrez API, BioC API  |
| Databases         |  Neo4j                 |
| NLP               |  spaCy                 |
| Embeddings        |  Transformer           |
| Cosine Similarity |  Scikit-learn          |
| Web Development   |  Streamlit             |
| Visualization     |  Matplotlib            |

## Group Details
* Group Name: Core-Code Crew
* Group Code: G23
* Tutor Responsible: Frederik, Hennecke
* Group team leader: Sreelakshmi, Ramesh
* Group Members: Kolakkattil, Gokul Prakash & Ramesh, Sreelakshmi  
