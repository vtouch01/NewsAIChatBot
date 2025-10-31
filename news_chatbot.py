# news_chatbot.py


import requests
import json
import os

# --- Configuration ---
# You need to get a free API key from NewsAPI (https://newsapi.org/)
# and replace 'YOUR_NEWS_API_KEY' below.
# It's best practice to use an environment variable, but for simplicity,
# we'll place it here.
API_KEY = "2fd3ce0df50c4552b1a86b8fac319ce8"
BASE_URL = "https://newsapi.org/v2/top-headlines"

def fetch_headlines(country_code, category):
    """Fetches top headlines for a given country and category."""
    if API_KEY == "YOUR_NEWS_API_KEY":
        print("ERROR: Please replace 'YOUR_NEWS_API_KEY' in the script with your actual NewsAPI key.")
        return None

    params = {
        'country': country_code,
        'category': category,
        'apiKey': API_KEY,
        'pageSize': 5  # Limit to 5 headlines for conciseness
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return data['articles']
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching news: {e}")
        print("Please check your internet connection or your API key.")
        return None

def display_headlines(articles, region, category):
    """Prints the fetched articles to the console."""
    print(f"\n--- Top 5 {category.capitalize()} Headlines in {region.upper()} ---")
    if not articles:
        print("No articles found.")
        return

    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No Title')
        source = article.get('source', {}).get('name', 'Unknown Source')
        url = article.get('url', 'No URL')

        print(f"{i}. {title}")
        print(f"   Source: {source}")
        print(f"   URL: {url}")
        print("-" * 20)

def main_chatbot_loop():
    """The main interactive loop for the chatbot."""
    print("\n👋 Welcome to the AI News Chatbot Agent!")
    print("You are running version 1.0.0.")
    print("Available Commands:")
    print("  'us news' - Get top U.S. headlines (General)")
    print("  'world news' - Get top World headlines (General)")
    print("  'us tech' - Get top U.S. Technology headlines")
    print("  'world business' - Get top World Business headlines")
    print("  'categories' - See all available categories")
    print("  'exit' or 'quit' - Close the chatbot")
    print("-" * 40)

    while True:
        user_input = input("Enter your news request (e.g., 'us news'): ").strip().lower()

        if user_input in ['exit', 'quit']:
            print("Thank you for using the News Chatbot. Goodbye! 👋")
            break
        elif user_input == 'categories':
            print("\nAvailable Categories (can be appended to 'us' or 'world' requests):")
            print("  business, entertainment, general, health, science, sports, technology")
            continue
        elif user_input == 'us news':
            articles = fetch_headlines(country_code='us', category='general')
            display_headlines(articles, 'US', 'General')
        elif user_input == 'world news':
            # NewsAPI uses 'country' codes. 'gb' (UK) is a good proxy for major English-language World News.
            articles = fetch_headlines(country_code='gb', category='general')
            display_headlines(articles, 'WORLD (UK Proxy)', 'General')
        elif user_input == 'us tech':
            articles = fetch_headlines(country_code='us', category='technology')
            display_headlines(articles, 'US', 'Technology')
        elif user_input == 'world business':
            articles = fetch_headlines(country_code='gb', category='business')
            display_headlines(articles, 'WORLD (UK Proxy)', 'Business')
        else:
            print("I don't recognize that command. Please try 'us news', 'world news', or 'categories'.")

if __name__ == "__main__":
    main_chatbot_loop()