import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import tweepy  # type: ignore

load_dotenv()

# Environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


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
    """# Enhanced Twitter Agent Prompt

    ## Function Description
    Create and post tweets on X (Twitter) platform based on user prompts with confirmation workflow.

    ## Parameters
    - **text** (str): Tweet content to be posted
    - **user_confirmation** (bool): Whether user has approved the tweet for posting

    ## Returns
    - **str**: Success message with tweet ID or error message with details

    ## Workflow Process

    ### 1. Content Generation
    - Generate engaging tweet content based on user's topic/request
    - Ensure tweet follows X platform guidelines (character limits, appropriate content)
    - Add relevant hashtags and mentions if applicable
    - Optimize for engagement (clear, concise, compelling)

    ### 2. Preview & Confirmation
    - Display the generated tweet to user for review
    - Ask for explicit confirmation before posting
    - Allow user to request modifications if needed
    - Handle approval/rejection gracefully

    ### 3. Posting & Response
    - Post tweet only after user confirmation
    - Provide success confirmation with tweet details
    - Handle errors gracefully with helpful messages

    ## Example Interaction

    **User**: "Hey, tweet on X with topic: I built an agent using LangChain and LangGraph"

    **Agent Response**:
    ```
    I've prepared a tweet for you about your LangChain and LangGraph agent! Here's what I've created:

    🚀 Just built an intelligent agent using LangChain and LangGraph! The combination of these frameworks made it incredibly smooth to create complex workflows with memory, reasoning, and tool integration. Excited to share what's possible with modern AI orchestration! 🤖⚡

    #LangChain #LangGraph #AI #MachineLearning #AgentDevelopment #TechInnovation

    Would you like me to post this tweet? Reply with 'yes' to confirm or suggest any changes you'd like me to make.
    ```

    **User**: "Yes, post it"

    **Agent**:
    ```
    ✅ Tweet posted successfully!

    Your tweet about LangChain and LangGraph agent has been published to your X timeline. You can view it at: [tweet_url]

    Tweet ID: [tweet_id]
    Posted at: [timestamp]

    Great work on building that agent! 🎉
    ```

    ## Enhanced Features

    ### Content Optimization
    - **Character count management**: Ensure tweets stay within X's limits
    - **Hashtag suggestions**: Add 3-5 relevant hashtags for better reach
    - **Tone matching**: Adapt writing style to user's preference (professional, casual, technical)
    - **Engagement optimization**: Use emojis, questions, or call-to-actions when appropriate

    ### Error Handling
    - **Network issues**: Retry mechanism with exponential backoff
    - **API rate limits**: Queue tweets and notify user of delays
    - **Content violations**: Suggest modifications for policy compliance
    - **Authentication errors**: Clear guidance for reconnection

    ### Additional Capabilities
    - **Thread creation**: For longer content, offer to create tweet threads
    - **Media attachment**: Support for images, GIFs, or polls
    - **Scheduling**: Option to schedule tweets for optimal posting times
    - **Analytics**: Basic engagement tracking and reporting

    ## Safety & Compliance
    - Verify content doesn't violate X platform policies
    - Respect user privacy and data
    - Handle authentication securely
    - Provide clear opt-out mechanisms

    ## Error Messages Examples
    - `❌ Error: Tweet exceeds character limit. Please shorten your message.`
    - `❌ Error: Unable to post due to network issues. Retrying in 30 seconds...`
    - `❌ Error: Content may violate platform guidelines. Please review and modify.`
    - `✅ Success: Tweet posted! View at: [URL]`"""

    # Credentials check
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        return "❌ Error: Twitter API credentials missing. Set environment variables."

    try:
        # Authentication
        x_auth = tweepy.OAuth1UserHandler(
            API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, CLIENT_ID, CLIENT_SECRET
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
