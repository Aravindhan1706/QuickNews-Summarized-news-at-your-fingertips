import streamlit as st
from PIL import Image
from transformers import pipeline
from newspaper import Article
import requests
import time

# Load summarizer model from Hugging Face Transformers
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to fetch top news articles from News API
def get_news_from_api(api_key):
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Error fetching news: {response.status_code}")
        return []
    
    articles = response.json().get('articles', [])
    return articles

# Function to summarize article content
def summarize_text(text):
    input_length = len(text.split())
    max_len = max(30, int(input_length * 0.5))  # Minimum 30, or half the input length
    try:
        summary = summarizer(text, max_length=max_len, min_length=15, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return None
# Function to display news articles
def display_news(list_of_news, news_quantity):
    c = 0
    for news in list_of_news:
        if news['title'] == "[Removed]":
            continue
        
        try:
            news_data = Article(news['url'])
            news_data.download()
            news_data.parse()
            news_data.nlp()

            # Display article image if available
            if news_data.top_image:
                # Generate summary
                summary = summarize_text(news_data.text)
                if summary:
                    # Display title and image
                    st.write(f"**({c + 1}) {news['title']}**")
                    st.image(news_data.top_image, use_column_width=True)
                    with st.expander(news['title']):
                        st.markdown(f"<p style='text-align: justify;'>{summary}</p>", unsafe_allow_html=True)
                        st.markdown(f"[Read more at source]({news['url']})")
                    st.success("Published Date: " + news['publishedAt'])
                else:
                    continue  # Skip if summarization fails
            else:
                continue  # Skip if no image is available
            
            c += 1
            if c >= news_quantity:
                break

        except Exception:
            continue  # Skip article if any error occurs

# Main Streamlit app function
def run():
    st.title("QuickNews: Summarized news at your fingertips")
    image = Image.open(r"images\news_logo.png")  # Path to your logo image
    st.image(image, use_column_width=False)

    st.subheader("Stay Informed, Stay Ahead – News Summarized for You")
    no_of_news = st.slider('Number of News:', min_value=1, max_value=8, step=1)
    api_key = '1eb9c435f7da448d9810651dcd912a90'  # Replace with your API key
    
    news_list = get_news_from_api(api_key)
    display_news(news_list, no_of_news)

run()
