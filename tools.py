import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import tweepy  # type: ignore
from system_prompt import tweet_prompt

load_dotenv()

# Environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")


@tool()
def get_weather(city: str):
    """this tool return weather data about city name"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return f"Weather in {city} is {response.text}"
        else:
            return f"Cannot fetch {city} data sorry!"
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"


@tool()
def web_search(query: str):
    """If the user query cannot be answered from the LLM knowledge base or context,
    invoke the web Search Query tool with the query text. Return results using the tool output.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID}

    try:
        response = requests.get(url, params=params)
        results = response.json()

        informations = []
        if "items" in results:
            for item in results["items"]:
                informations.append(
                    f"{item['title']}: {item['link']}\n{item.get('snippet', '')}"
                )

        return "\n\n".join(informations[:5])  # Top 5 results
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool()
def tweet_on_x(text: str):
    """IMPORTANT => follow this prompt {tweet_prompt}"""

    # Credentials check
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        return "❌ Error: Twitter API credentials missing. Set environment variables."

    try:
        # Authentication
        x_auth = tweepy.OAuth1UserHandler(
            API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
        )
        api = tweepy.API(x_auth, wait_on_rate_limit=True)

        # Verify credentials
        api.verify_credentials()

        # Tweet length validation
        if len(text) > 280:
            return f"❌ Error: Tweet too long ({len(text)}/280 characters)"

        if len(text.strip()) == 0:
            return "❌ Error: Tweet cannot be empty"

        # Post tweet
        response = api.update_status(status=text)

        return f"✅ Tweet posted successfully!\n📍 Tweet ID: {response.id}\n🔗 URL: https://twitter.com/{response.user.screen_name}/status/{response.id}"

    except tweepy.Unauthorized:
        return "❌ Error: Invalid credentials or app permissions"
    except tweepy.Forbidden as e:
        if "duplicate" in str(e).lower():
            return "❌ Error: Duplicate tweet not allowed"
        elif "rate limit" in str(e).lower():
            return "❌ Error: Rate limit exceeded. Try after some time"
        else:
            return f"❌ Error: Access forbidden - {str(e)}"
    except tweepy.BadRequest as e:
        return f"❌ Error: Bad request - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
