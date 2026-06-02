import os
from datetime import UTC, datetime
from dotenv import load_dotenv
load_dotenv()

#langsmith Debug

print("LANGSMITH_API_KEY:", bool(os.getenv("LANGSMITH_API_KEY")))
print("LANGSMITH_TRACING:", os.getenv("LANGSMITH_TRACING"))
print("LANGSMITH_TRACING_V2:", os.getenv("LANGSMITH_TRACING_V2"))
print("LANGSMITH_PROJECT:", os.getenv("LANGSMITH_PROJECT"))

#import mongo db
from pymongo import MongoClient
from langsmith import traceable
from langchain_google_genai import GoogleGenerativeAI

#MongoDB
import certifi

# Replace your current mongo_client block with this:
mongo_client = MongoClient(
    os.getenv("MONGODB_URI"),
    tlsCAFile=certifi.where()
)
mongo_client.admin.command("ping")

db = mongo_client["AI_AGENT"]

#create connections

chat_collection = db["chat_history"]
print("MongoDB connection successfully")

#Gemini
llm = GoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
    )

#mongo DB Save Info
@traceable(name="MongoDB_save")
def save_chat(question, answer):
    chat_collection.insert_one(
        {
            "question": question,
            "answer": answer,
            "created_at": datetime.now(UTC)
        }
    )

#MongoDB Save Traceable
@traceable(
        run_type="chain",
        name = "GeminiMongoAgent"
)

def ask_agent(question):
    print("Tracing Question", question)
    response = llm.invoke(question)
    answer=response
    save_chat(question, answer )
    return answer

print("\n Gemini Agent Started")
print("come out exit or quit to stop the agent \n")

#While loop with exception handling
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        response = ask_agent(user_input)
        print("Agent: ", response)
    except Exception as e:
        print("An error occurred:", str(e))