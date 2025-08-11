# 🤖 AI Chatbot with Tools

A powerful Streamlit-based AI chatbot application that integrates weather data, web search capabilities, and persistent conversation history

## ✨ Features

- **🔧 Tool Integration**: Weather data retrieval and web search functionality
- **📱 Chat History Sidebar**: Manage multiple conversation threads
- **🔄 Real-time Streaming**: Live response generation with loading indicators
- **🎨 Clean UI**: Modern Streamlit interface with chat bubbles
- **⚡ Error Handling**: Robust error management and user feedback

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Groq (Moonshot AI Kimi-K2-Instruct)
- **Framework**: LangChain + LangGraph
- **APIs**: Google Custom Search, OpenWeatherMap-style API

1. **Clone the repository**

```bash
git clone <https://github.com/surjanthakur/GPT-burrito.git>
cd persona
```

2. **Install dependencies**
   pip install -r requirements.txt

**Weather Queries:**

```
"What's the weather in New York?"
"How's the weather in London today?"
```

**Web Search Queries:**

```
"Latest news about AI"
"Python programming tutorials"
"Current stock price of Tesla"
```

### Managing Chats

- **Switch Chats**: Click on any chat in the sidebar
- **Delete Chats**: Click the 🗑️ button next to any chat
- **New Chat**: Use the "➕ New Chat" button

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Streamlit UI  │────│  LangGraph   │────│   MongoDB   │
│                 │    │   Engine     │    │ Checkpoints │
└─────────────────┘    └──────────────┘    └─────────────┘
         │                       │
         │                       │
    ┌─────────┐            ┌─────────────┐
    │  User   │            │    Tools    │
    │ Input   │            │ - Weather   │
    └─────────┘            │ - Web Search│
                           └─────────────┘
```

### Key Components

- **State Management**: TypedDict-based state for message handling
- **Graph Structure**: START → Chatbot → Tools → Chatbot (conditional)
- **Checkpointing**: MongoDB-based conversation persistence
- **Tool Routing**: Automatic tool selection based on user queries

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: This README

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the AI framework
- [Streamlit](https://streamlit.io/) for the web interface
- [Groq](https://groq.com/) for fast AI inference

---

**Made with ❤️ by surjan thakur**
