import os
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Get the API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the embedding function
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Load and process documents
documents = []
transcript_dir = "yt-transcripts"

print("Loading documents...")
for filename in tqdm(os.listdir(transcript_dir)):
    if filename.endswith(".txt"):
        file_path = os.path.join(transcript_dir, filename)
        loader = TextLoader(file_path)
        documents.extend(loader.load())

print(f"Loaded {len(documents)} documents.")

print("Splitting documents into chunks...")
texts = text_splitter.split_documents(documents)
print(f"Created {len(texts)} text chunks.")

print("Creating vector store... This may take a while.")
start_time = time.time()

# Process in smaller batches
batch_size = 500  # Adjust this value if needed
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

for i in tqdm(range(0, len(texts), batch_size)):
    batch = texts[i:i+batch_size]
    vectorstore.add_documents(documents=batch)
    
    # Print progress every 10 minutes
    if i % (batch_size * 12) == 0 and i > 0:
        elapsed_time = time.time() - start_time
        progress = i / len(texts)
        estimated_total_time = elapsed_time / progress
        estimated_remaining_time = estimated_total_time - elapsed_time
        print(f"\nProgress: {progress:.2%}")
        print(f"Elapsed time: {elapsed_time / 3600:.2f} hours")
        print(f"Estimated time remaining: {estimated_remaining_time / 3600:.2f} hours")
        
    # Persist every 100 batches to save progress
    if i % (batch_size * 100) == 0 and i > 0:
        print("\nSaving progress...")
        vectorstore.persist()
        print("Progress saved.")

end_time = time.time()
total_time = end_time - start_time
print(f"\nVector store creation completed in {total_time / 3600:.2f} hours.")

print("Persisting final vector store...")
vectorstore.persist()

print("Vector store created and persisted successfully.")