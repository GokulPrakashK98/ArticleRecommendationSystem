from neo4j import GraphDatabase
import bcrypt
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
    
    def close(self):
        if self.__driver:
            self.__driver.close()
    
    def query(self, query, parameters=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session:
                session.close()
        return response
    
########### User Authentication #############
def register_user(conn, first, last, username, password):
    """Register a new user in Neo4j."""
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        conn.query("""
        CREATE CONSTRAINT user_unique_username IF NOT EXISTS
        FOR (u:User) REQUIRE u.username IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)

    query = """
    CREATE (u:User {first_name:$first, last_name: $last, username: $username, password: $password})
    """
    conn.query(query, parameters={"username": username, "password": hashed_pw, 'first': first, 'last': last})
    return True

def fetch_users(conn):
    """Fetch all user information"""
    query = "MATCH (u:User) RETURN u.first_name AS first_name, u.last_name as last_name, u.username AS user_name"
    results = conn.query(query)
    user_info = {}
    for items in results:
        first_name = items['first_name']
        last_name = items['last_name']
        user_name = items['user_name']
        user_info[user_name] = {'first_name': first_name, 'last_name': last_name}
    user_lst = list(user_info.keys())
    return user_info, user_lst

def verify_user(conn, username, password):
    """Verify user credentials."""
    query = """
    MATCH (u:User {username: $username})
    RETURN u.password AS password
    """
    result = conn.query(query, parameters={"username": username})
    if result:
        stored_password = result[0]["password"]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    return False

def add_selected(conn, selected, user, keyword):
    """Add user seletced article to database"""
    try:
        conn.query("""
        CREATE CONSTRAINT article_id IF NOT EXISTS
        FOR (a:Article) REQUIRE a.article_id IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)

    # Adding selected article
    article_id = selected['pmcid']
    title = selected['Title']
    abstract = selected['Abstract']
    query = f"""
    MERGE (a:Article {{pmcid: $article_id}})
    ON CREATE SET a.title = $title, a.abstract = $abstract, a.created_at = timestamp()
    WITH a
    MATCH (u:User {{username: $user_name}})
    MERGE (u)-[r:SELECTED {{keyword:$keyword}}]->(a)
    ON CREATE SET r.created_at = timestamp()
    """
    # Run the query
    try:
        conn.query(query, parameters={
            'article_id': article_id,
            'title': title,
            'abstract': abstract,
            'user_name': user,
            'keyword':keyword
        })
    except Exception as e:
        print("Error adding article or relationship:", e)

def add_recommended(conn, recommended, selected, user):
    """Add recommended articles for the user 
       seletced article to database"""
    try:
        conn.query("""
        CREATE CONSTRAINT article_id IF NOT EXISTS
        FOR (r:RecomArticle) REQUIRE r.article_id IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)
    selected_id  = selected['pmcid']
    for id, item in recommended.items():
        article_id = id
        similarity = round(item['similarity_score'], 4)
        title = item['title']
        abstract = item['abstract']

        query = f"""
        MERGE (r:RecomArticle {{article_id: $article_id}})
        ON CREATE SET r.title = $title, r.abstract = $abstract, r.similarity_score = $similarity
        WITH r
        MATCH (u:User {{username: $user_name}})-[:SELECTED]->(a:Article {{pmcid: $selected_id}})
        MERGE (a)-[:RECOMMENDED]->(r)
        """
        # Run the query
        try:
            conn.query(query, parameters={
                'article_id': article_id,
                'title': title,
                'abstract': abstract,
                'user_name': user,
                'similarity':similarity,
                'selected_id':selected_id
            })
        except Exception as e:
            print("Error adding article or relationship:", e)

def fetch_history(conn, user_name):
    query = f"""
    MATCH (u:User {{username: $user_name}})-[s:SELECTED]->(a:Article)
    RETURN s.keyword AS search_term, a.pmcid AS pmcid, a.title AS title
    ORDER BY s.created_at DESC
    LIMIT 5
    """
    try:
        result = conn.query(query, parameters={
            'user_name': user_name})
        return result
    except Exception as e:
        print(f"Error occured while fetching history: {e}")

def remove_user(conn, username):
    query = f"""
    MATCH (u:User {{username: $user_name}}) DETACH DELETE u
    """
    try:
        result = conn.query(query, parameters={
            'user_name': username})
        return result
    except Exception as e:
        print(f"Error occured while removing user: {e}")

def get_statistics(conn):
    query = """
    MATCH (u:User)
    WITH count(u) AS user_count

    MATCH (a:Article) 
    WITH  user_count, count(a) AS selected_article_count

    MATCH (r:RecomArticle)
    RETURN user_count, selected_article_count, count(r) AS recom_article_count
    """
    try:
        result = conn.query(query)
        return result[0]
    except Exception as e:
        print(f"Error occured while fetching history: {e}")


def plot_statistics(stats):
    if not stats:
        st.write("No data available for plotting.")
        return
    
    labels = ['Users', 'Selected Articles', 'Recommended Articles']
    values = stats

    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=['blue', 'green', 'orange'])])

    fig.update_layout(
        title="Neo4j Database Statistics",
        xaxis_title="Categories",
        yaxis_title="Count",
        bargap=0.2
    )

    st.plotly_chart(fig)  
