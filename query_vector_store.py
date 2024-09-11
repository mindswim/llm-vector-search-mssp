import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

# Get the API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Load the persisted vector store
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Initialize the language model
llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=openai_api_key)

# Create a retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
)

# Query the system
query = input("Enter your query: ")
result = qa_chain.run(query)
print(result)