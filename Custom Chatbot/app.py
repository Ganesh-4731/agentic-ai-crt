from flask import Flask,render_template,request,jsonify
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os 


#flask instance
app=Flask(__name__)

#config ur model gemini 2.5 flash
genai.configure(api_key=os.getenv("Gemini_API_Key"))


model =genai.GenerativeModel("gemini-2.5-flash")


df =pd.read_csv("my_qa.csv")
context_text =""


for _,row in df.iterrows():
    context_text += f"""
Q:{row['question']}
A:{row['answer']}
"""
#ask gemini function
def ask_gemini(query):
    prompt=f""" 
You are a Q/A assistant,

Answer ONLY isng the context below.

if the answer is not present ,say: 

NO relevent A&A found.

Context: {context_text}

Question:
{query}
"""
    response=model.generate_content(prompt)
    return response.text.strip()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask",methods=["POST"])
def ask():
    data=request.get_json()

    user_query = data ['query']
    answer = ask_gemini(user_query)
    return jsonify({
        "answer":answer

    })

if __name__ == "__main__":
    app.run(debug=True)