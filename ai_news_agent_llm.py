# ai_news_agent.py - Version 3.1.0 with Keyword Search

import requests
import ollama
import json
import textwrap
import sys

# --- Configuration ---
# You need to get a free API key from NewsAPI (https://newsapi.org/)
# and replace 'YOUR_NEWS_API_KEY' below.
API_KEY = "2fd3ce0df50c4552b1a86b8fac319ce8"
LLM_MODEL = "llama3-groq-tool-use" # Ensure this model is downloaded via 'ollama run llama3'

# --- News Tool Definitions (for LLM Function Calling) ---

def fetch_top_headlines(country: str, category: str) -> str:
    """
    Fetches the top news headlines from NewsAPI for a specified country and category.
    The country must be a 2-letter code (e.g., 'us', 'gb').
    The category must be one of: 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'.
    """
    if API_KEY == "YOUR_NEWS_API_KEY":
        return json.dumps({"error": "NewsAPI key is not configured."})

    BASE_URL = "https://newsapi.org/v2/top-headlines"
    
    country = country.lower().strip()
    category = category.lower().strip()
    
    # Use 'gb' (Great Britain/UK) as a robust proxy for global English news
    if country == 'world':
        country = 'gb'

    params = {
        'country': country,
        'category': category,
        'apiKey': API_KEY,
        'pageSize': 3  # Limit to 3 for quick agent execution
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])

        # Format output for the LLM to easily summarize
        formatted_articles = [
            {
                "title": a.get('title'), 
                "content": a.get('content', 'No content available.')
            }
            for a in articles if a.get('content') # Only include articles with content
        ]
        
        return json.dumps(formatted_articles)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to fetch top headlines. Check API Key or internet: {e}"})

def search_news_by_keyword(query: str, language: str = 'en') -> str:
    """
    Searches all news sources using a specific keyword or phrase.
    This is best for searching specific topics, companies, or people.
    The language must be a 2-letter ISO-639-1 code (e.g., 'en', 'de').
    """
    if API_KEY == "YOUR_NEWS_API_KEY":
        return json.dumps({"error": "NewsAPI key is not configured."})

    BASE_URL = "https://newsapi.org/v2/everything"
    
    params = {
        'q': query,
        'language': language.lower().strip(),
        'apiKey': API_KEY,
        'pageSize': 3, # Limit to 3 for quick agent execution
        'sortBy': 'relevancy' # Sort by best match for the keyword
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])

        # Format output for the LLM to easily summarize
        formatted_articles = [
            {
                "title": a.get('title'), 
                "content": a.get('content', 'No content available.')
            }
            for a in articles if a.get('content') # Only include articles with content
        ]
        
        return json.dumps(formatted_articles)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to perform keyword search. Check API Key or internet: {e}"})

# Define ALL tools available to the LLM
TOOLS = [fetch_top_headlines, search_news_by_keyword]
TOOL_MAP = {func.__name__: func for func in TOOLS}


# --- Agent Core Logic (Unchanged from previous version) ---

def run_agent(user_prompt: str):
    """The main agent loop that handles LLM reasoning and tool execution."""
    print(f"\n🧠 Agent reasoning on prompt: '{user_prompt}'...")
    
    # 1. Initial Agent Call: Decide whether to use a tool
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': user_prompt}],
            tools=TOOLS, # Pass both tools to the LLM
            options={'temperature': 0.5}
        )
    except Exception as e:
        print(f"\n*** CRITICAL ERROR ***\nFailed to connect to Ollama. Ensure the Ollama application is running and '{LLM_MODEL}' is downloaded.\nError: {e}")
        return

    # 2. Check for Tool Use 
    #tool_calls = response.get('tool_calls', [])
    response_message = response.message
    tool_calls = response.message.tool_calls

    if tool_calls:
        print(f"🛠️ Tool requested: The Agent plans to call {len(tool_calls)} tool(s).")
        
        # 3. Execute the Tool Call(s)
        tool_outputs = []
        for call in tool_calls:
            func_name = call['function']['name']
            func_args = call['function']['arguments']
            
            if func_name in TOOL_MAP:
                # Execute the defined function with the arguments chosen by the LLM
                print(f"   Executing: {func_name}({func_args})")
                
                # Dynamically call the function from the map
                tool_result = TOOL_MAP[func_name](**func_args)
                
                tool_outputs.append({
                  #  "tool_call_id": call['id'],
                    "output": tool_result,
                })

        # 4. Second Agent Call: Send results back to the LLM for final summary
        print("🧠 Sending tool results back to LLM for summarization...")
        
        # Add the tool outputs to the messages history
        messages_with_tool_outputs = [
            {'role': 'user', 'content': user_prompt},
            response['message'], # The LLM's message with tool_calls
            {'role': 'tool', 'tool_outputs': tool_outputs}
        ]

        final_response = ollama.chat(
            model=LLM_MODEL,
            messages=messages_with_tool_outputs,
            options={'temperature': 0.3}
        )

        # 5. Display the final LLM summary
        print("-" * 60)
        print("✨ AI Agent Summary:")
        wrapped_summary = textwrap.fill(final_response['message']['content'].strip(), subsequent_indent='  ')
        print(wrapped_summary)
        print("-" * 60)

    else:
        # The LLM decided the request didn't need a tool (e.g., "hello")
        print("📢 Agent Response (No tool needed):")
        print(response['message']['content'].strip())


# --- Main Loop ---

def main_agent_loop():
    """The main interactive loop for the AI Agent."""
    print("\n🤖 Welcome to the AI News Agent (Keyword Search Added)!")
    print("Version 3.1.0 (Ollama Llama 3 Agent).")
    print("---------------------------------------------------------------")
    print("Ask natural language questions. The Agent will decide when to use the best tool.")
    print("Example prompts:")
    print("  - What's the latest in US sports news? (Uses fetch_top_headlines)")
    print("  - **Tell me about the new Microsoft product.** (Uses search_news_by_keyword)")
    print("  - Hello, how are you?")
    print("  - 'exit' or 'quit' - Close the agent")
    print("-" * 60)

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            print("Thank you for using the AI News Agent. Goodbye! 👋")
            break
        
        if not user_input:
            continue

        run_agent(user_input)

if __name__ == "__main__":
    main_agent_loop()