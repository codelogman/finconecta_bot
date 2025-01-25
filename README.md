# AI Engineer Challenge - Chatbot with RAG Pipeline

This repository contains the implementation of a chatbot designed to meet the objectives of the AI Engineer challenge. The system uses a custom web scraping tool to gather product data, processes this data using embeddings, and integrates it into a Retrieval-Augmented Generation (RAG) pipeline to provide accurate answers to user queries.

## Objectives of the Challenge

The primary goal of this project is to demonstrate an efficient chatbot that can query a product database (scraped from a website) and generate accurate responses without relying on pre-existing large-scale generative models. The solution leverages:

- Web scraping for data collection.
- Embeddings for semantic search.
- A Retrieval-Augmented Generation pipeline for enhanced response generation.

The chatbot responds to natural language queries about products by retrieving relevant information from the scraped dataset and generating insightful responses based on the stored data.

## How the Scraper and Pipeline Integrate

### Scraper:
The scraper is implemented using a Python script that collects product information (name, price, description, category, and URL) from the website [http://books.toscrape.com/](http://books.toscrape.com/). The scraped data is then stored in a CSV file, which is used as input for the pipeline.

### Embeddings:
Once the CSV file is generated, the data is processed to extract embeddings using Hugging Face models. The embeddings are then indexed with FAISS, allowing for fast retrieval of relevant information when a user submits a query.

### RAG Pipeline:
The Retrieval-Augmented Generation (RAG) pipeline combines the retrieved information with generative models to formulate comprehensive answers. The pipeline works by:
1. Searching the FAISS index to find relevant product data based on the query.
2. Using Hugging Face models to generate a response that synthesizes the retrieved data.

### Integration:
The scraper, embeddings, and RAG pipeline are integrated to create a seamless flow. The scraper collects data, the embeddings are generated and indexed, and the chatbot uses the indexed data to respond to user queries effectively.

## Detailed Explanation of the Code

1. **Scraper**:
   - The scraper script fetches data from the website and saves it as a CSV file.
   - Error handling is implemented to ensure the scraper runs smoothly even if some products are unavailable or the website structure changes.

2. **Embeddings & FAISS Indexing**:
   - Data from the CSV file is processed using Hugging Face models to generate embeddings.
   - These embeddings are indexed using FAISS, ensuring efficient and fast retrieval.

3. **Chatbot (Gradio Interface)**:
   - A user-friendly interface is created using Gradio, where users can input natural language queries.
   - The chatbot processes these queries, retrieves relevant data, and generates a response.

4. **Error Handling & Efficiency**:
   - Robust error handling ensures that failures in scraping or model inference do not affect the user experience.
   - The pipeline is designed to handle small datasets effectively, allowing for faster responses and less overhead.

## Potential Improvements and Alternatives

While the current system works effectively for the scope of this challenge, there are several areas where the solution could be improved:

1. **Scaling Up**:
   - If the volume of data were to increase, the system could benefit from using distributed scraping and indexing techniques.
   - Using more powerful generative models (e.g., GPT-3 or GPT-4) could improve the quality and depth of the responses.

2. **API Integration**:
   - The chatbot could be enhanced by integrating generative APIs such as OpenAI's GPT models, allowing for more sophisticated conversation flows.
   - External APIs could be used for real-time data retrieval, such as updating product prices or availability.

3. **Handling Larger Datasets**:
   - To handle larger datasets, optimizing the FAISS index and exploring other indexing methods (e.g., HNSW) would increase retrieval efficiency.
   - Implementing batching and parallel processing for embedding generation could also help.

4. **User Feedback Loop**:
   - Incorporating user feedback into the system could improve response accuracy over time, allowing the chatbot to learn from interactions.

## Conclusion

This project demonstrates how a chatbot can be implemented using a custom scraping tool, embeddings, and a Retrieval-Augmented Generation pipeline. It showcases efficient techniques for semantic search and response generation, and it offers a solid foundation for future improvements such as the integration of generative APIs and handling larger datasets.

## Installation

To run the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-engineer-challenge.git
