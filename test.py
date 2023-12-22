import numpy as np
import streamlit as st
import sqlite3
import os
import pandas as pd
import requests

header_sticky = """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: white;
            z-index: 999;
        }
        .fixed-header { 
        }
    </style>
        """

def display_existing_messages():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def add_user_message_to_session(prompt):
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

def add_bot_message_to_session(response):
    if response:
        st.session_state["messages"].append({"role": "ai", "content": response})
        with st.chat_message("ai"):
            st.markdown(response)

def call_api(prompt):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer nv-k60PAgXcL3VCAMszaCLpN0V4x0SSpS2VDS7Ba8AdqWJBtY0x',
    }

    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    }

    response = requests.post('https://api.nova-oss.com/v1/chat/completions', headers=headers, json=json_data)
    return response.json()

def chat():
    chat_container = st.container()
    chat_container.header("ChatUIT", divider="rainbow")
    
    ### Custom CSS for the sticky header
    chat_container.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
    st.markdown(header_sticky, unsafe_allow_html=True)
    
    
    display_existing_messages()
    query = st.chat_input("Say something")
    if query:
        add_user_message_to_session(query)
        result = call_api(query)
        response = result['choices'][0]['message']['content']
        add_bot_message_to_session(response)
      

def sidebar():
    with st.sidebar:
        st.header('**Database**', divider='rainbow')
        list_db = os.listdir('database/')   
        db = st.selectbox('**Select Database**', list_db)
            
        
        conn = sqlite3.connect(f'database/{db}/{db}.sqlite')
        cursor = conn.cursor()
        
        with st.expander('Tables'):
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            list_table = [i[0] for i in cursor.fetchall()]
            df = pd.DataFrame(list_table, columns=['Table Name'])
            st.write(df)    
        try:
            sql_query = st.text_area('**SQL Query**')
            cursor.execute(sql_query)
            list_data = cursor.fetchall()
            columns = next(zip(*cursor.description))
            df = pd.DataFrame(list_data, columns=columns)
            st.write(df)
        except:
            # write red color markdown
            if sql_query != "":
                st.markdown('<p style="color:red;">🙉 Error sql query!!!</p>', unsafe_allow_html=True)
    conn.close()
    
if __name__ == "__main__":
    chat()
    sidebar()

