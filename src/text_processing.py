import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

def textrank_summarize(text, num_sentences=5):
    # Tokenize sentences
    sentences = text.split('.')
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    # Create sentence embeddings
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentence_embeddings = model.encode(sentences)
    
    # Compute similarity matrix
    similarity_matrix = cosine_similarity(sentence_embeddings)
    
    # Create graph
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    
    # Rank sentences
    ranked_sentences = sorted(((scores[i], sentence) 
                                for i, sentence in enumerate(sentences)), 
                               reverse=True)
    
    # Return top sentences
    summary = '. '.join([sent for score, sent in ranked_sentences[:num_sentences]])
    return summary