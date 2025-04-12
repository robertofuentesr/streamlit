import streamlit as st
import requests
import pandas as pd
import altair as alt
import re
from collections import Counter

@st.cache_data
def load_text(url):
    """Download the text from the URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        st.error("Error fetching the text!")
        return ""

def process_text(text):
    """
    Process the text: remove punctuation, convert to lowercase,
    and count the frequency of each word (ignoring words with less than 2 letters).
    """
    # Use a regular expression to only capture words (alphabetic characters) of length 2 or more.
    words = re.findall(r'\b[a-z]{2,}\b', text.lower())
    return Counter(words)

def main():
    st.title("Word Frequency Visualizer")
    st.write("This Streamlit app reads a text from Project Gutenberg and shows the most popular words.")

    # URL to the text file on Project Gutenberg
    url = "https://www.gutenberg.org/cache/epub/22367/pg22367.txt"
    
    # Load and display basic info about the text
    text = load_text(url)
    if text:
        st.success("Text loaded successfully!")
    else:
        st.stop()  # Stop the app if the text couldn't be loaded
    
    # Process the text to get word frequencies
    word_counts = process_text(text)
    
    # Convert the Counter dictionary into a DataFrame
    df = pd.DataFrame(word_counts.items(), columns=["Word", "Frequency"])
    df = df.sort_values(by="Frequency", ascending=False).head(1000)  # Top 20 words

    st.write("### Top 20 Most Frequent Words")
    st.dataframe(df)

    # Create a bar chart using Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Frequency:Q", title="Frequency"),
        y=alt.Y("Word:N", sort='-x', title="Word"),
        tooltip=["Word", "Frequency"]
    ).properties(
        width=600,
        height=400,
        title="Popular Words in the Text"
    )

    st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    main()
