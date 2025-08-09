# 🤖 AI Chatbot with Tools & MongoDB Persistence

A powerful Streamlit-based AI chatbot application that integrates weather data, web search capabilities, and persistent conversation history using MongoDB checkpointing.

## ✨ Features

- **🔧 Tool Integration**: Weather data retrieval and web search functionality
- **💾 MongoDB Persistence**: Conversation history stored and retrieved automatically
- **📱 Chat History Sidebar**: Manage multiple conversation threads
- **🔄 Real-time Streaming**: Live response generation with loading indicators
- **🎨 Clean UI**: Modern Streamlit interface with chat bubbles
- **⚡ Error Handling**: Robust error management and user feedback

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Groq (Moonshot AI Kimi-K2-Instruct)
- **Framework**: LangChain + LangGraph
- **Database**: MongoDB (for conversation persistence)
- **APIs**: Google Custom Search, OpenWeatherMap-style API

## 📋 Prerequisites

- Python 3.8+
- MongoDB instance running (local or remote)
- API Keys:
  - Groq API Key
  - Google Custom Search API Key
  - Google Custom Search Engine ID

## 🚀 Installation

1. **Clone the repository**

```bash
git clone <https://github.com/surjanthakur/GPT-burrito.git>
cd persona
```

2. **Install dependencies**

```bash
pip install streamlit langchain langgraph groq pymongo python-dotenv requests
```

3. **Set up environment variables**

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
GROQ_API_KEY=your_groq_api_key
```

4. **Configure MongoDB**

Update the MongoDB connection string in the code if needed:

```python
DB_URL = "mongodb://admin:admin@host.docker.internal:27017"
```

For local MongoDB:

```python
DB_URL = "mongodb://localhost:27017"
```

## 🔧 API Setup

### Google Custom Search API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create credentials and get your API key
4. Set up a Custom Search Engine at [Google CSE](https://cse.google.com/)

### Groq API

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up and get your API key
3. Add it to your `.env` file

### MongoDB Setup

**Option 1: Local MongoDB**

```bash
# Install MongoDB locally
# macOS
brew install mongodb-community

# Ubuntu
sudo apt-get install mongodb

# Start MongoDB
mongod
```

**Option 2: Docker MongoDB**

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin \
  mongo:latest
```

**Option 3: MongoDB Atlas (Cloud)**

1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string and update `DB_URL`

## 🏃‍♂️ Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 📖 Usage

### Starting a Chat

1. Click "➕ New Chat" in the sidebar
2. Type your message in the chat input
3. The AI will respond with relevant information

### Using Tools

The chatbot automatically uses tools when needed:

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

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection Error**

```
Error: pymongo.errors.ServerSelectionTimeoutError
```

**Solution**: Check MongoDB is running and connection string is correct

**API Key Errors**

```
Error: Invalid API key
```

**Solution**: Verify all API keys in `.env` file are correct

**Tool Not Working**

```
Error: Tool execution failed
```

**Solution**: Check internet connection and API quotas

### Debug Mode

Add debug information by setting Streamlit to debug mode:

```bash
streamlit run app.py --logger.level=debug
```

## 🔒 Security Notes

- Keep API keys secure and never commit `.env` files
- Use MongoDB authentication in production
- Consider rate limiting for public deployments
- Validate user inputs for production use

## 📝 Configuration

### Customizing Tools

Add new tools by creating functions with the `@tool()` decorator:

```python
@tool()
def my_custom_tool(parameter: str):
    """Tool description"""
    # Your tool logic here
    return result
```

### Changing Models

Update the model in the `initialize_graph()` function:

```python
llm = init_chat_model(
    model_provider="groq",
    model="your-preferred-model",
    api_key=GROQ_API_KEY,
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: This README
- **Community**: [Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the AI framework
- [Streamlit](https://streamlit.io/) for the web interface
- [Groq](https://groq.com/) for fast AI inference
- [MongoDB](https://mongodb.com/) for conversation persistence

---

**Made with ❤️ by surjan thakur**
