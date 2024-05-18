import streamlit as st
import openai
#client = OpenAI()

st.title("simple chat")

user_message = st.text_input(label="どうしましたか？")

if user_message:
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": user_message}
    ],
    )
    st.write(completion.choices[0].message["content"])