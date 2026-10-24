#standard library imports
import os
import json


#Third part imports
from openai import OpenAI
from dotenv import load_dotenv
from types import SimpleNamespace


#Local modules
from tools import TOOLS, run_tool
from Utilities.utilities import log

load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages= []

MAX_STEPS = 5

messages.append(
    {
        "role":"system",
        "content": (
    "You are a helpful, humble assistant. "
    "Answer general questions (programming, science, advice) from your own knowledge. "
    "Use a tool ONLY when the user asks for the current time, the weather, or their city. "
    "Keep answers under 100 words."
)
    }
)

def stream_chat(history):
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools= TOOLS,
        stream=True
    )

    full_response="" 
    calls={}
    label_printed= False

    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            #content streaming
            if delta.content:
                if not label_printed:
                    print("Assistant: ", end="", flush=True)
                    label_printed=True

                print(delta.content, end="", flush=True)
                full_response += delta.content

            #2. tool calls
            for tc in (delta.tool_calls or []):
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments

    except KeyboardInterrupt:
     print("\n {Stopped By You}")
     calls = {}

    if label_printed:
        print()
    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])
        
    return full_response, calls_list

def build_tool_calls_payload(tool_calls):
    """
    converts our collected tool calls into the dict format that the API expects inside an assistant mssg
    """
    payload =[]
    for tool_call in tool_calls:
        tool_call_dict = {
            "id":tool_call.id,
            "type":"function",
            "function":{
                "name":tool_call.function.name,
                "arguments":tool_call.function.arguments,
            },
        }
        payload.append(tool_call_dict)
    return payload


while True:

    user_input = input("\nShashwat: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append({
        "role":"user",
        "content":user_input
    })    

    #chained tool calling
    for step in range(MAX_STEPS):

        full_response, tool_calls = stream_chat(messages)
        
        #msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"Step {step+1}: model requested {len(tool_calls)}")

        messages.append(
            {"role":"assitant", "content":full_response, "tool_calls":build_tool_calls_payload(tool_calls)}
        )

        for tool_call in tool_calls:
                  
            result = run_tool(tool_call)

            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id, 
                "content":str(result),
            })

    else:
        fallback = "Sorry, I couldn't finish this within the step limit."
        messages.append({
                "role":"assistant",
                "content":fallback
            })
        print("Assitant: " + fallback)
        continue

messages.append({
        "role":"assistant",
        "content":full_response
    })
    

    
   