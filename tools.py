import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


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
    """if the user search query data not exist in llm data then call this internet search quwry tool"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID}

    try:
        res = requests.get(url, params=params)
        results = res.json()

        informations = []
        if "items" in results:
            for item in results["items"]:
                informations.append(
                    f"{item['title']}: {item['link']}\n{item.get('snippet', '')}"
                )

        return "\n\n".join(informations[:3])  # Top 3 results
    except Exception as e:
        return f"Error performing web search: {str(e)}"
