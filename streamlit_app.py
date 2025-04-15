import streamlit as st
import requests
import pandas as pd
import altair as alt
import spacy
import re
from collections import Counter
from bs4 import BeautifulSoup 

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
    """Download and clean text from the URL."""
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'  # Force UTF-8 encoding
        if response.status_code == 200:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            # Get text content with proper spacing
            text = soup.get_text(separator='\n', strip=True)
            
            # Remove excessive empty lines
            cleaned_text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
            cleaned_text = re.sub(r'\b\w*\d\w*\b', '', cleaned_text)
            return cleaned_text
            
        else:
            st.error(f"Error: HTTP Status {response.status_code}")
            return ""
            
    except Exception as e:
        st.error(f"Error fetching content: {str(e)}")
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

def identifying_level(level,dictionary,df):
    dictionary_df = pd.read_csv(dictionary)
    df = df.merge(dictionary_df[['word','level']], how='left', on=['word'] )
    df = df.fillna("C2")
    level_dictionary = {"A1":1, 
                        "A2":2,
                        "B1":3,
                        "B2":4,
                        "C1":5,
                        "C2":6,}
    df['level_number'] = df['level']
    df['level_number'] = df['level_number'].apply(lambda x: level_dictionary[x])
    # we select a higher or equal level
    df = df[df["level_number"]>=level_dictionary[level]]
    df.drop(["level_number"], axis=1, inplace=True)
    return df
def main():
    st.title("Word Frequency Visualizer")
    st.write("""This Streamlit app reads a text/url in German
            and shows you only the words you probably don't know. 
            Currently, this is a beta version (maybe even an alpha (?)). 
            So it may show some words that are easy at C2-level. 
            Gauging which words you truly know thou, JUST based on your level is tricky. Because it 
            depends on what you've read or studied to reach that level.
            without further ado, give it a shot :) """)

    # URL to the text file on Project Gutenberg
    #url = "https://www.gutenberg.org/cache/epub/22367/pg22367.txt"
    # Input field for the URL
    url = st.text_input("Enter a URL:")
    level = st.text_input("Enter your level: A1, A2, B1, B2, C1, C2")
    # Load and display basic info about the text
    if url and level:  # Only execute if url and level are not empty
        st.write(f"""This is the website: {url}""")
        # Load and display basic info about the text
        text = load_text(url)

        # Load SpaCy German model
        nlp = spacy.load("de_core_news_sm")

        # Extract nouns, adjectives, and verbs
        nouns = extract_words_by_pos(text, nlp, "NOUN")

        adjectives = extract_words_by_pos(text, nlp, "ADJ")
        verbs = extract_words_by_pos(text, nlp, "VERB")

        noun_counts = list_to_pandas(nouns)
        adjective_counts = list_to_pandas(adjectives)
        verb_counts = list_to_pandas(verbs)


        # joining
        noun_counts = identifying_level(level,"noun_counts_total.csv",noun_counts)
        adjective_counts = identifying_level(level,"adjective_counts_total.csv",adjective_counts)
        verb_counts = identifying_level(level,"verb_counts_total.csv",verb_counts)

        # Display results and visualizations for nouns
        st.write(f"### Extracted {len(nouns)} nouns.")
        st.dataframe(noun_counts, width=1000)
        # Display results and visualizations for adjectives
        st.write(f"### Extracted {len(adjectives)} adjectives.")
        st.dataframe(adjective_counts, width=1000)
        # Display results and visualizations for verbs
        st.write(f"### Extracted {len(verbs)} verbs.")
        st.dataframe(verb_counts, width=1000)

        # Convert the dataframe to CSV
        download(noun_counts)
        download(adjective_counts,"adjetives")
        download(verb_counts,"verbs")
        st.write(f"""If you have fun using this and want to donate I'll give you the option (paypal). Maybe you would be the first one :)""")
        

    else:
        st.write("Please enter a URL to begin")






if __name__ == '__main__':
    main()