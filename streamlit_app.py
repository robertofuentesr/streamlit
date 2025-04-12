import streamlit as st

# Title of the app
st.title("Welcome to My Streamlit App!")

# User input
name = st.text_input("Enter your name:")

# Button to generate a greeting
if st.button("Say Hello"):
    if name:
        st.write(f"Hello, {name}! 🎉 Welcome to the world of Streamlit.")
    else:
        st.write("Hello, Stranger! 😊 Please enter your name.")

# Optional information
st.markdown("This is a simple starter app to help you get familiar with Streamlit.")
