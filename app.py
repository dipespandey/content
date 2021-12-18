import sys
import time
import json
import numpy as np
import pandas as pd
from sqlalchemy.orm import session
from tensorflow.python.keras.backend import placeholder
import chatbot.preprocessor as p
from tensorflow.keras.models import load_model
import joblib
from pathlib import Path 
from PIL import Image
import streamlit as st
from chatbot import SessionState

sys.path.append('..')
from data_retrieval.database_queries import *

#paths
img_path = Path.joinpath(Path.cwd(),'chatbot/images')
artifacts_path = Path.joinpath(Path.cwd(),'chatbot/model_artifacts')
datasets_path = Path.joinpath(Path.cwd(),'chatbot/dataset')

#load images 
center = Image.open(Path.joinpath(img_path,'ntnubanner.webp'))
logo_image = Image.open(Path.joinpath(img_path,'ntnulogo.png'))
# nadal =Image.open(Path.joinpath(img_path,'Nadal.jpg'))

#load artifacts 
model = load_model(Path.joinpath(artifacts_path,'model-v1.h5'))
tokenizer_t = joblib.load(Path.joinpath(artifacts_path,'tokenizer_t.pkl'))
vocab = joblib.load(Path.joinpath(artifacts_path,'vocab.pkl'))

df2 = pd.read_csv(Path.joinpath(datasets_path,'response.csv'), quotechar='`')

ss = SessionState.get(is_startup=True, course='') 

def get_pred(model,encoded_input):
    pred = np.argmax(model.predict(encoded_input))
    return pred


def bot_precausion(df_input,pred):
    words = df_input.questions[0].split()
    if len([w for w in words if w in vocab])==0 :
        pred = 1
    return pred


def get_response(df2,pred):
    print(df2.response)
    upper_bound = df2.groupby('labels').get_group(pred).shape[0]
    r = np.random.randint(0,upper_bound)
    responses = list(df2.groupby('labels').get_group(pred).response)
    return responses[r]


def botResponse(user_input):
    df_input = user_input
    
    df_input = p.remove_stop_words_for_input(p.tokenizer, df_input, 'questions')
    encoded_input = p.encode_input_text(tokenizer_t, df_input, 'questions')

    pred = get_pred(model, encoded_input)
    pred = bot_precausion(df_input, pred)
    response = get_response(df2, pred)
    try:
        # check if it is a json object
        db_responses = json.loads(response)
        response = convert_intent_json_to_response_string(db_responses)
    except Exception as e:
        # else it is a string
        print(e)
        # response = "Sorry, I couldn't catch that one!"
    
    # response = bot_response(response)
    
    # if ss.is_startup:
    #     response = "Hi, I'm a NTNU chatbot. You can ask me about all the courses available."
    #     ss.is_startup = False
    #     return response

    # else:
    return response


def get_text():
    input_text = st.text_input("You: ","type here")
    df_input = pd.DataFrame([input_text],columns=['questions'])
    return df_input 


def db_response(user_input):
    # set context for general and specific queries
    user_input_queries = user_input.questions.tolist()
    if user_input_queries[0] in ['hello', 'hi']:
        return intro_response()
    
    elif user_input_queries[0].isnumeric():
        # set context for specific queryf
        course_id = int(user_input_queries[0])
        ss.course = course_id
        print(ss.course)
        return get_course_by_id(course_id)

    else:
        if isinstance(ss.course, int):
            if 'other' in user_input_queries[0]:
                ss.course = ''
                return get_all_courses()
            else:
                course_object = get_course_object_by_id(ss.course)
                output = get_attribute_of_a_program(course_object, user_input_queries[0])
                if not output:
                    ss.course = ''
                    return "Sorry, couldn't catch that one! " 
                else:
                    return output       
        return botResponse(user_input)


st.sidebar.title("")
st.title("""
NTNU Chatbot   
NTNU Chatbot is a NLP bot trained using basic NTNU course data catalog using CNN achitecture
""")

st.image(center,width=700)
st.sidebar.image(logo_image, width=200)

user_input = get_text()

first = time.perf_counter()

user_input_queries = user_input.questions.tolist()
with open('conversation.txt', 'a') as f:
    if len(user_input_queries)>0 and user_input_queries[0] != 'type here':
        f.write(f'\nQ: {user_input_queries[0]}')
    
print('\n\n\nuserinput is: \n\n\n\n', user_input_queries)
print('course selected is: ', ss.course)
print('\n\n\n')
if 'type here' not in user_input_queries and len(user_input_queries[0])>0:
    response = db_response(user_input)
    st.text_area("Bot:", value=response, height=200, max_chars=None, key=None)
    print('response is', response)
    with open('conversation.txt', 'a') as f:
        f.write(f'\nA: {response}')
    
    last = time.perf_counter()
    with open('timer.txt', 'a') as f:
        f.write(f'\n{last-first}')
else:
    st.text_area("Bot:", value='', height=200, max_chars=None, key=None, placeholder='Hello there!')
