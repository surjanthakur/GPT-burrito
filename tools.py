import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

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
def send_email_tool(to: str, subject: str, body: str):
    """Send an email to the given address."""
    sender_email = os.getenv("EMAIL_ADDRESS") or ""
    sender_password = os.getenv("EMAIL_PASSWORD") or ""

    msg = MIMEText(body)
    msg["subject"] = subject
    msg["from"] = sender_email or ""
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, msg.as_string())
        return f"Email sent successfully to {to}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
