import streamlit as st
import requests
import pandas as pd
import altair as alt
import re
from collections import Counter

@st.cache_resource
def load_model():
    """Load the SpaCy German model."""
    return spacy.load("de_core_news_sm")

def extract_words_by_pos(text, nlp, pos):
    """
    Extract words of a specific part of speech from the text using SpaCy.
    """
    doc = nlp(text)
    words = [token.lemma_ for token in doc if token.pos_ == pos]
    return words
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
    st.write("""This Streamlit app reads a text from Project Gutenberg
             and shows the most popular words.""")

    # URL to the text file on Project Gutenberg
    url = "https://www.gutenberg.org/cache/epub/22367/pg22367.txt"
    st.write(f"""This is the website: {url}""")
    # Load and display basic info about the text
    text = load_text(url)
    if text:
        st.success("Text loaded successfully!")
    else:
        st.stop()  # Stop the app if the text couldn't be loaded
    
    # Load SpaCy German model
    nlp = load_model()

    # Extract nouns, adjectives, and verbs
    nouns = extract_words_by_pos(text, nlp, "NOUN")
    adjectives = extract_words_by_pos(text, nlp, "ADJ")
    verbs = extract_words_by_pos(text, nlp, "VERB")

    # Display results and visualizations for nouns
    st.write(f"### Extracted {len(nouns)} nouns.")
    noun_counts = pd.DataFrame(pd.Series(nouns).value_counts(), columns=["Frequency"]).reset_index()
    noun_counts.rename(columns={"index": "Noun"}, inplace=True)
    top_nouns = noun_counts.head(20)
    st.write("### Top 20 Most Frequent Nouns")
    st.dataframe(top_nouns)

    noun_chart = alt.Chart(top_nouns).mark_bar().encode(
        x=alt.X("Frequency:Q", title="Frequency"),
        y=alt.Y("Noun:N", sort='-x', title="Noun"),
        tooltip=["Noun", "Frequency"]
    ).properties(
        width=600,
        height=400,
        title="Top 20 Nouns in the Text"
    )
    st.altair_chart(noun_chart, use_container_width=True)

    # Display results and visualizations for adjectives
    st.write(f"### Extracted {len(adjectives)} adjectives.")
    adj_counts = pd.DataFrame(pd.Series(adjectives).value_counts(), columns=["Frequency"]).reset_index()
    adj_counts.rename(columns={"index": "Adjective"}, inplace=True)
    top_adjectives = adj_counts.head(20)
    st.write("### Top 20 Most Frequent Adjectives")
    st.dataframe(top_adjectives)

    adj_chart = alt.Chart(top_adjectives).mark_bar().encode(
        x=alt.X("Frequency:Q", title="Frequency"),
        y=alt.Y("Adjective:N", sort='-x', title="Adjective"),
        tooltip=["Adjective", "Frequency"]
    ).properties(
        width=600,
        height=400,
        title="Top 20 Adjectives in the Text"
    )
    st.altair_chart(adj_chart, use_container_width=True)

    # Display results and visualizations for verbs
    st.write(f"### Extracted {len(verbs)} verbs.")
    verb_counts = pd.DataFrame(pd.Series(verbs).value_counts(), columns=["Frequency"]).reset_index()
    verb_counts.rename(columns={"index": "Verb"}, inplace=True)
    top_verbs = verb_counts.head(20)
    st.write("### Top 20 Most Frequent Verbs")
    st.dataframe(top_verbs)

    verb_chart = alt.Chart(top_verbs).mark_bar().encode(
        x=alt.X("Frequency:Q", title="Frequency"),
        y=alt.Y("Verb:N", sort='-x', title="Verb"),
        tooltip=["Verb", "Frequency"]
    ).properties(
        width=600,
        height=400,
        title="Top 20 Verbs in the Text"
    )
    st.altair_chart(verb_chart, use_container_width=True)

if __name__ == '__main__':
    main()