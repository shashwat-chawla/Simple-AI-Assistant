from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages= []

messages.append(
    {
        "role":"system",
        "content":"Act like a very humble agent and always respond under 40 words."
    }
)

while True:

    user_input = input("\nShashwat: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append({
        "role":"user",
        "content":user_input
    })    

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    messages.append({
            "role":"assistant",
            "content":response.choices[0].message.content
        })  

    
    print("Assistant: " + response.choices[0].message.content)
   