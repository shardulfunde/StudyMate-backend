from sqlalchemy.orm import Session
from app.db.models.resource_embedding import ResourceEmbedding
from sqlalchemy.sql.expression import func
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_cohere import CohereEmbeddings


model = CohereEmbeddings(model="embed-english-v3.0")


#I love to name these things lol
#Python is all you need
def get_random_chunks_from_topic(db:Session,resource_id:str):
    random_chunks = db.query(ResourceEmbedding.chunk_text).filter(ResourceEmbedding.resource_id==resource_id).order_by(func.random()).limit(20).all()
    chunk_list = []
    for chunk in random_chunks:
        chunk_list.append(chunk.chunk_text)
    
    return chunk_list

#Function for everything
def get_random_chunks_from_subject(db:Session,subject_id:str):
    random_chunks = db.query(ResourceEmbedding.chunk_text).filter(ResourceEmbedding.subject_id==subject_id).order_by(func.random()).limit(20).all()
    chunk_list = []
    for chunk in random_chunks:
        chunk_list.append(chunk.chunk_text)
    
    return chunk_list

#Similiarity search hell yeah
def get_relevant_chunks_for_test(db:Session,resource_id:str,query:str):
    """Retrieval by similiarity search for test generation"""
    query_embedding = model.embed_query(query)
    relevant_chunks = db.query(ResourceEmbedding.chunk_text).filter(ResourceEmbedding.resource_id==resource_id).order_by(ResourceEmbedding.embedding.cosine_distance(query_embedding)).limit(20).all()
    chunk_list = []
    for chunk in relevant_chunks:
        chunk_list.append(chunk.chunk_text)
    return chunk_list

#Similiarity search for subject
def get_relevant_chunks_for_subject(db:Session,subject_id:str,query:str):
    """Retrieval by similiarity search for subject"""
    #Docstrings are cool
    query_embedding = model.embed_query(query)
    relevant_chunks = db.query(ResourceEmbedding.chunk_text).filter(ResourceEmbedding.subject_id==subject_id).order_by(ResourceEmbedding.embedding.cosine_distance(query_embedding)).limit(20).all()
    chunk_list = []
    for chunk in relevant_chunks:
        chunk_list.append(chunk.chunk_text)
    return chunk_list   