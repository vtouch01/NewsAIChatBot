# news_chatbot_llm.py

import requests
import ollama
import json
import textwrap

# --- Configuration ---
# You need to get a free API key from NewsAPI (https://newsapi.org/)
# and replace 'YOUR_NEWS_API_KEY' below.
API_KEY = "2fd3ce0df50c4552b1a86b8fac319ce8"
BASE_URL = "https://newsapi.org/v2/top-headlines"
LLM_MODEL = "llama3"  # Ensure this model is downloaded via 'ollama run llama3'

def fetch_and_summarize_headlines(country_code, category):
    """Fetches news and uses local LLM (via Ollama) to summarize."""
    if API_KEY == "YOUR_NEWS_API_KEY":
        print("ERROR: Please replace 'YOUR_NEWS_API_KEY' in the script with your actual NewsAPI key.")
        return None

    # 1. Fetch Headlines
    print(f"\n🌍 Fetching top {category.capitalize()} headlines for {country_code.upper()}...")
    params = {
        'country': country_code,
        'category': category,
        'apiKey': API_KEY,
        'pageSize': 3  # Reduced to 3 for faster LLM processing
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching news: {e}")
        return None

    # 2. Summarize each article using Ollama
    summarized_articles = []
    
    if not articles:
        print("No articles found to summarize.")
        return summarized_articles

    print(f"🧠 Summarizing {len(articles)} articles with {LLM_MODEL}...")
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No Title')
        content = article.get('content')
        
        # We only summarize articles that have content
        if content:
            # Craft a concise prompt for the LLM
            prompt = f"Please provide a concise, two-sentence summary of the following news article for a software engineer:\n\nTITLE: {title}\n\nCONTENT: {content}"
            
            try:
                # Call the local Ollama API
                llm_response = ollama.chat(
                    model=LLM_MODEL,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                    options={'temperature': 0.1} # Lower temp for factual summarization
                )
                
                summary = llm_response['message']['content'].strip()
            except Exception as e:
                summary = f"[LLM ERROR: Could not summarize content. Ensure Ollama is running and the model '{LLM_MODEL}' is downloaded.]"
                print(f"Warning: LLM API error for article {i}: {e}")
        else:
            summary = "No content available to summarize."
        
        article['summary'] = summary
        summarized_articles.append(article)

    return summarized_articles

def display_summaries(articles, region, category):
    """Prints the LLM-generated summaries to the console."""
    print(f"\n--- Top {len(articles)} {category.capitalize()} Summaries in {region.upper()} ---")
    if not articles:
        print("No articles found or successfully summarized.")
        return

    for i, article in enumerate(articles, 1):
        source = article.get('source', {}).get('name', 'Unknown Source')
        url = article.get('url', 'No URL')

        print(f"**{i}. {article.get('title', 'No Title')}**")
        print(f"   Source: {source}")
        
        # Wrap summary text for neatness in the terminal
        wrapped_summary = textwrap.fill(article.get('summary', 'Summary unavailable.'), initial_indent='   Summary: ', subsequent_indent='            ')
        print(wrapped_summary)
        print(f"   URL: {url}")
        print("-" * 60)

def main_chatbot_loop():
    """The main interactive loop for the chatbot."""
    print("\n🤖 Welcome to the LLM-Powered News Chatbot Agent!")
    print("Version 2.0.0 (using Ollama and Llama 3 for summarization).")
    print("---------------------------------------------------------------")
    print("Available Commands:")
    print("  'us news' - Get top 3 U.S. headlines (Summarized)")
    print("  'world tech' - Get top 3 World Technology headlines (Summarized)")
    print("  'exit' or 'quit' - Close the chatbot")
    print("-" * 60)

    while True:
        user_input = input("Enter your news request (e.g., 'us news'): ").strip().lower()

        if user_input in ['exit', 'quit']:
            print("Thank you for using the News Chatbot. Goodbye! 👋")
            break
        elif user_input == 'us news':
            articles = fetch_and_summarize_headlines(country_code='us', category='general')
            display_summaries(articles, 'US', 'General')
        elif user_input == 'world tech':
            # 'gb' (UK) is used as a proxy for major English-language World Tech news.
            articles = fetch_and_summarize_headlines(country_code='gb', category='technology')
            display_summaries(articles, 'WORLD (UK Proxy)', 'Technology')
        else:
            print("I don't recognize that command. Please try 'us news' or 'world tech'.")

if __name__ == "__main__":
    # Ensure Ollama is accessible before starting the loop (optional but helpful)
    try:
        ollama.list()
        main_chatbot_loop()
    except Exception as e:
        print("\n\n*** CRITICAL ERROR ***")
        print("Failed to connect to Ollama. Please ensure the Ollama application is installed, running, and the 'llama3' model is downloaded.")
        print(f"Error details: {e}")
