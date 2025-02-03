from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
import torch
import numpy as np

def vectorize_text(texts_lst, method='bert'):
    # Choose one methods
    if method == 'tfidf':
        vectorizer = TfidfVectorizer(stop_words='english')
        return vectorizer.fit_transform(texts_lst)
    elif method == 'bert':
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertModel.from_pretrained('bert-base-uncased')
        inputs = tokenizer(texts_lst, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()
    

def get_similar_articles(selected_abstract, all_abstracts, method='bert'):
    # Vectorize both the selected abstract and all abstracts
    all_abstracts.append(selected_abstract)
    vectors = vectorize_text(all_abstracts, method)
    # Convert it into array
    if method == 'tfidf':
        vectors = vectors.toarray() 
    # Calculate cosine similarity (last added vector is the selected article)
    similarity = cosine_similarity([vectors[-1]], vectors[:-1])
    return similarity.flatten()

def get_recommendation(similarity_scores, df):
    # Sorting the similarity scores in descending order
    sorted_indices = np.argsort(similarity_scores)[::-1]
    # Number of top similar articles to display
    top_5_dict = {} 
    for idx in sorted_indices[:10]:
        score = similarity_scores[idx]
        pmcid = df.loc[idx, 'pmcid']
        title = df.loc[idx, 'Title']
        abstract = df.loc[idx, 'Abstract']
        top_5_dict[pmcid] = {
                'similarity_score': score,
                'pmcid': pmcid,
                'title': title,
                'abstract': abstract}
    return top_5_dict

def display_recommended(article_df, recommend, keys, section, rec):
    df = article_df[article_df['pmcid']==keys]
    rec.write(f"Similarity score: {recommend[keys]['similarity_score']}")
    rec.write(f"PMCID: {recommend[keys]['pmcid']}")
    rec.write(f"Title: {recommend[keys]['title']}")
    rec.text_area(f"**{section}:**", df[section].iloc[0], height=250)
    return recommend[keys]

