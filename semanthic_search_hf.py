import os
import faiss
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel, pipeline
from tqdm import tqdm
import gradio as gr
import re

from huggingface_hub import login

# Authenticate with Hugging Face to access the models
login(token="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")

# Load the CSV file containing product data
df = pd.read_csv('products.csv')

# Remove duplicate rows based on name and description
df = df.drop_duplicates(subset=['name', 'description'])

# Convert the price column to numeric by removing any non-numeric characters
df['price'] = df['price'].replace('[^\d.]', '', regex=True).astype(float)

# Load the tokenizer and model for sentence embeddings
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Function to generate embeddings for a given text
def generate_embedding(text):
    """
    Generate a sentence embedding for the input text using the pre-trained model.

    Args:
        text (str): Input text to be converted into an embedding.

    Returns:
        numpy.ndarray: A vector representation of the input text.
    """
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embeddings

# Function to truncate long text inputs for better readability
def shorten_input(text, max_length=100):
    """
    Truncate the input text to a maximum length and append ellipses if truncated.

    Args:
        text (str): The text to be shortened.
        max_length (int): Maximum allowed length.

    Returns:
        str: Truncated text.
    """
    return text[:max_length] + "..." if len(text) > max_length else text

# Extract price threshold from user queries (e.g., "under 50" or "below $20")
def extract_price_threshold(query):
    """
    Extract a price threshold from a query if specified.

    Args:
        query (str): User input query.

    Returns:
        int or None: Extracted price threshold or None if not present.
    """
    match = re.search(r'under\s*\$?(\d+)|below\s*\$?(\d+)', query, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return None

# Perform FAISS similarity search with a minimum similarity threshold
def safe_similarity_search(query, similarity_threshold=0.5):
    """
    Perform a similarity search using FAISS with an optional similarity threshold.

    Args:
        query (str): User input query.
        similarity_threshold (float): Minimum similarity score to consider.

    Returns:
        list: List of matching documents or an empty list if none are found.
    """
    try:
        query_embedding = generate_embedding(query).astype('float32')
        k = 5  # Number of closest documents to retrieve
        D, I = index.search(query_embedding, k)

        # Filter results by similarity threshold
        docs = [docstore.search(str(i)) for i, d in zip(I[0], D[0]) if d >= similarity_threshold]
        return docs
    except Exception as e:
        print(f"Error during similarity search: {e}")
        return []

# Initialize a text generation pipeline using GPT-2
text_generation_pipeline = pipeline("text-generation", model="openai-community/gpt2", tokenizer="openai-community/gpt2")

# Validate the relevance of a user query
def is_relevant_query(query):
    """
    Check if the query contains relevant keywords for the domain.

    Args:
        query (str): User input query.

    Returns:
        bool: True if relevant, False otherwise.
    """
    keywords = ["book", "price", "category", "description"]
    return any(keyword in query.lower() for keyword in keywords)

# Generate an answer for the user's query
def generate_answer(query):
    """
    Generate a response based on the user's query using similarity search and GPT-2.

    Args:
        query (str): User input query.

    Returns:
        str: Generated answer or a fallback message.
    """
    if not is_relevant_query(query):
        return "Your query doesn't seem related to the domain. Please ask about books, prices, or categories."

    # Perform similarity search
    docs = safe_similarity_search(query, similarity_threshold=0.5)

    if docs:
        # Check for a price threshold in the query
        price_threshold = extract_price_threshold(query)
        if price_threshold is not None:
            # Filter results by the specified price threshold
            docs = [doc for doc in docs if float(doc['price']) <= price_threshold]
            if not docs:
                return f"No books found under ${price_threshold}."

        # Construct the context for the answer
        context = "\n".join([
            f"Name: {doc['name']} | Price: {doc['price']} | Description: {shorten_input(doc['description'], max_length=100)}"
            for doc in docs
        ])

        # Generate a response using the GPT-2 model
        prompt = f"Answer the following question based on the following context: {context}. Question: {query}"
        answer = text_generation_pipeline(
            prompt,
            max_new_tokens=70,
            num_return_sequences=1,
            temperature=0.7
        )
        
        # Clean and return the generated answer
        output = format_output(answer[0]['generated_text'])
        return output.strip()
    else:
        return "No relevant documents found for your query."

# Format output by removing noise and irrelevant text
def format_output(output):
    """
    Clean up the generated text to focus only on structured results.

    Args:
        output (str): Generated text output.

    Returns:
        str: Cleaned output.
    """
    lines = output.splitlines()
    formatted_lines = [line.strip() for line in lines if line.startswith("Name:")]
    return "\n".join(formatted_lines)

# Embedding dimensions for the pre-trained model
dimension = 384

# Remove any previous FAISS index
index_file = "faiss_index.index"
if os.path.exists(index_file):
    os.remove(index_file)
    print("Previous FAISS index removed.")

# Create a new FAISS index
index = faiss.IndexFlatL2(dimension)
print("New FAISS index created.")

# Generate embeddings and populate the FAISS index
metadata = []
embeddings_batch = []

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating embeddings", ncols=100):
    if not row['description']:
        print(f"Warning: Description missing for product {row['name']}. Skipping...")
        continue

    text = f"{row['name']} {row['category']} {row['description']} {row['price']}"
    embedding = generate_embedding(text).astype('float32')
    embeddings_batch.append(embedding)
    metadata.append({
        'id': str(idx),
        'name': row['name'],
        'price': row['price'],
        'description': row['description'],
        'category': row['category']
    })

embeddings_batch = np.vstack(embeddings_batch)

# Verify synchronization and save to FAISS
if len(embeddings_batch) == len(metadata):
    index.add(embeddings_batch)
    faiss.write_index(index, index_file)
    print("Embeddings loaded and saved to FAISS successfully.")
else:
    print(f"Error: Number of embeddings ({len(embeddings_batch)}) does not match metadata ({len(metadata)}). Check data.")

# Define a custom document store class
class CustomDocStore:
    def __init__(self, metadata):
        self.metadata = metadata

    def search(self, doc_id):
        return next((item for item in self.metadata if item['id'] == doc_id), None)

# Initialize the document store
docstore = CustomDocStore(metadata)

# Launch the Gradio interface for user interaction
iface = gr.Interface(fn=generate_answer, inputs=gr.Textbox(label="Question"), outputs="text", title="QA Generative Bot")
iface.launch(share=True)

