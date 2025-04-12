import streamlit as st
import requests
import pandas as pd
import altair as alt
import spacy
import re
from collections import Counter
import warnings

def download(df,name="nouns"):
    csv = df.to_csv(index=False)
    st.download_button(
    label=str(f"Download {name} as CSV"),
    data=csv,
    file_name=str(f"{name}.csv"),
    mime="text/csv"
)
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
def list_to_pandas(nouns):
    word = list(pd.Series(nouns).value_counts().index)
    number_times = list(pd.Series(nouns).value_counts().values)
    df = pd.DataFrame({"word":word, "frequency": number_times })
    return df
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
    nlp = spacy.load("de_core_news_sm")

    # Extract nouns, adjectives, and verbs
    nouns = extract_words_by_pos(text, nlp, "NOUN")

    adjectives = extract_words_by_pos(text, nlp, "ADJ")
    verbs = extract_words_by_pos(text, nlp, "VERB")

    # Display results and visualizations for nouns
    st.write(f"### Extracted {len(nouns)} nouns.")

    noun_counts = list_to_pandas(nouns)
    adjective_counts = list_to_pandas(adjectives)
    verb_counts = list_to_pandas(verbs)

    st.dataframe(noun_counts)


    # Display results and visualizations for adjectives
    st.write(f"### Extracted {len(adjectives)} adjectives.")
    st.dataframe(adjective_counts)
    st.write("### Top 20 Most Frequent Adjectives")
    st.dataframe(noun_counts)

    # Display results and visualizations for verbs
    st.write(f"### Extracted {len(verbs)} verbs.")
    st.dataframe(verb_counts)

    # Convert the dataframe to CSV

    download(noun_counts)
    download(adjective_counts,"adjetives")
    download(verb_counts,"verbs")



if __name__ == '__main__':
    main()