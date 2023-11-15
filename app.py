import os
import streamlit as st
from openai import OpenAI
#from keys import openAIapikey
import json
import random
import sys

def generate_characters(characters):
    response = ""
    for character in characters:
        response + f"{generate_character(**character)}\n\n"
    return response

def generate_character(name, age, gender, personality):
    return f"{name} is a {age} years old {gender}.\n{personality}"

def printResponse(response_message):
    if response_message.function_call:
        #Which function call was invoked?
        function_called = response_message.function_call.name
        
        #Extract the arguments from the AI payload
        function_args  = json.loads(response_message.function_call.arguments)
        
        #Create a list of all the available functions
        available_functions = {
            "generate_characters": generate_characters,
            #TODO add more functions here?
        }
        
        fuction_to_call = available_functions[function_called]

        #Call the function with the provided arguments
        response_message = fuction_to_call(function_args["characters"])
    else:
        #The LLM didn't call a function but provided a response
        response_message = response_message.content
    #Write the response
    st.subheader(response_message)

def main():
    #Set up the api key for OpenAI
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    #os.environ["OPENAI_API_KEY"] = openAIapikey

    #Initialize the Streamlit page
    st.set_page_config(
        page_title="Character List Generator",
        page_icon="🤖")
    
    #Set up the function that the LLM can call based on the prompt it is given
    custom_functions = [
    {
        'name': 'generate_characters',
        'description': 'Generate a group of random characters based on a short description',
        'parameters': {
            "type": "object",
            "properties": {
                "characters": {
                    'type': 'array',
                    "description": "A list of randomly generated characters",
                    "items": {
                        "type": "object",
                        "description": "A single randomly generated character",
                        'properties': {
                            'name': {
                                'type': 'string',
                                'description': 'Randomly generated name of the person'
                            },
                            'gender': {
                                'type': 'string',
                                "enum": ["Male", "Female", "Non-binary"],
                                'description': "The person's chosen gender"
                            },
                            'age': {
                                'type': 'integer',
                                'description': 'Age of the person'
                            },
                            'personality': {
                                'type': 'string',
                                'description': "A short description of the character, with no location or relationship data. Generate this from the user's name, age, and gender."
                            }
                        },
                        "required": ["name", "gender", "age", "personality"]
                    },
                },
            },
            "required": ["characters"]
        }
    },
]
    
    #Get the user's input
    container = st.container()
    with container:
        with st.form(key="my form", clear_on_submit=True):
            user_input  = st.text_area(label="Enter a short description of the group of characters: ", key="input", height = 100)
            submit_button = st.form_submit_button(label="Generate")

        client = OpenAI()
        if submit_button:
            descriptions = []
            if user_input:
                descriptions.append(user_input)
            else:
                #If the user doesn't enter any input, use a default prompt
                descriptions.append(f"A villager in a cozy little town")
                
            with st.spinner("Thinking..."):
                for description in descriptions:
                    #output the user's prompt
                    st.header(description)

                    #Use a seed so we can reproduce our results if we have to
                    seed = random.randint(0, sys.maxsize)
                    st.write(seed)

                    #Call the LLM...
                    response = client.chat.completions.create(
                        model = 'gpt-3.5-turbo',
                        temperature=1.4, #Use a really high temp so the LLM can get creative
                        seed=seed, #Include the seed
                        messages = [{'role': 'user', 'content': description}],
                        functions = custom_functions, #Pass in the list of functions available to the LLM
                        function_call = 'auto')
                    printResponse(response.choices[0].message) #Print the LLM response

if __name__ == "__main__":
    main()