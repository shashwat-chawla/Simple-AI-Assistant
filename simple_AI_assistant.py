from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP

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
        messages=messages,
        tools=TOOLS,
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
            result = fn(**func_args)

            messages.append({
                "role":"tool",
                "tool_id":tool_call.id,
                "content":str(result),
            })


        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )

        msg = response.choices[0].message

    messages.append({
        "role":"assistant",
        "content":msg.content
    })
    

    
    print("Assistant: " + msg.content)
   