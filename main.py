import os
import streamlit as st
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.mongodb import MongoDBSaver  # type: ignore
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from typing import Annotated, List
from dotenv import load_dotenv
import uuid
from datetime import datetime
from tools import get_weather, web_search
from system_prompt import system_prompt

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page config
st.set_page_config(
    page_title="AI Agent with Tools",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)


# Custom CSS for modern styling with custom color scheme
st.markdown(
    """
<style>
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #3E3F29 0%, #7D8D86 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: #F1F0E4;
        text-align: center;
        box-shadow: 0 4px 15px rgba(62, 63, 41, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
        color: #F1F0E4;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        color: #F1F0E4;
    }

    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #7D8D86 0%, #BCA88D 100%);
        color: black;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 3px 12px rgba(125, 141, 134, 0.4);
        border: 2px solid #BCA88D;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #BCA88D 0%, #F1F0E4 100%);
        color:black;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 3px 12px rgba(188, 168, 141, 0.3);
        border-left: 4px solid #7D8D86;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3E3F29 0%, #7D8D86 100%);
        color: #F1F0E4;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(62, 63, 41, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(62, 63, 41, 0.4);
        background: linear-gradient(135deg, #7D8D86 0%, #BCA88D 100%);
    }

    /* Current chat title */
    .current-chat-title {
        color: white;
    }

    /* Loading spinner styling */
    .stSpinner {
        color: #7D8D86;
    }
</style>
""",
    unsafe_allow_html=True,
)


class State(TypedDict):
    messages: Annotated[List, add_messages]


# chat model
llm = init_chat_model(
    model_provider="groq",
    model="moonshotai/kimi-k2-instruct",
    api_key=GROQ_API_KEY,
)

tools = [get_weather, web_search]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    PROMPT = system_prompt()
    messages_with_prompt = [SystemMessage(content=PROMPT)] + state["messages"]
    result = llm_with_tools.invoke(messages_with_prompt)
    return {"messages": result}


graph_builder = StateGraph(State)
tool_node = ToolNode(tools=tools)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")


# compile graph with checkpointing
def graph_with_checkpointing(checkpointer):
    compile_graph = graph_builder.compile(checkpointer=checkpointer)
    return compile_graph


# Initialize session state
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def create_new_chat():
    chat_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    chat_title = f"Chat {timestamp}"

    st.session_state.chat_history[chat_id] = {
        "title": chat_title,
        "messages": [],
        "created_at": timestamp,
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []


def load_chat(chat_id):
    if chat_id in st.session_state.chat_history:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chat_history[chat_id]["messages"]


def save_current_chat():
    if st.session_state.current_chat_id:
        st.session_state.chat_history[st.session_state.current_chat_id][
            "messages"
        ] = st.session_state.messages


def main():
    init_session_state()

    # Enhanced sidebar for chat history
    with st.sidebar:
        st.markdown(
            """
        <div class="sidebar-header">
            <h2>💬 Chat History</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # New chat button with custom styling
        st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Display chat history with enhanced styling
        if st.session_state.chat_history:
            st.markdown("### Recent Conversations")
            for chat_id, chat_data in reversed(
                list(st.session_state.chat_history.items())
            ):
                is_current = chat_id == st.session_state.current_chat_id

                st.markdown('<div class="chat-item">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        f"💭 {chat_data['title']}",
                        key=f"chat_{chat_id}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary",
                    ):
                        load_chat(chat_id)
                        st.rerun()

                with col2:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                        del st.session_state.chat_history[chat_id]
                        if chat_id == st.session_state.current_chat_id:
                            st.session_state.current_chat_id = None
                            st.session_state.messages = []
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("🎯 No chat history yet. Start a new conversation!")

        # Sidebar footer
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
        <div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem;">
            <p>🤖 AI Agent</p>
            <p>Weather • Web Search • Chat • Code</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Enhanced main chat interface
    st.markdown(
        """
    <div class="main-header">
        <h1>🤖 AI Agent with Tools</h1>
        <p>Ask me anything! I can search the Internet and Generate cool stuff for you !</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Create new chat if none exists
    if not st.session_state.current_chat_id:
        create_new_chat()

    # Display current chat title with enhanced styling
    if st.session_state.current_chat_id:
        current_chat = st.session_state.chat_history[st.session_state.current_chat_id]
        st.markdown(
            f"""
        <div class="current-chat-title">
            <h3>📝 {current_chat['title']}</h3>
            <small>Created: {current_chat['created_at']}</small>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Display chat messages with enhanced styling
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="user-message">
                    <strong>You:</strong><br>
                    {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Chat input
    if prompt := st.chat_input("💬 Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        st.markdown(
            f"""
        <div class="user-message">
            <strong>You:</strong><br>
            {prompt}
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Get bot response
        with st.spinner("🤔 Thinking and processing your request..."):
            try:
                # Create state with conversation history
                langchain_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        langchain_messages.append(HumanMessage(content=msg["content"]))
                    else:
                        langchain_messages.append(AIMessage(content=msg["content"]))

                state = State(messages=langchain_messages)

                # Get response from the graph
                response_container = st.empty()
                full_response = ""

                DB_URL = "mongodb://admin:admin@host.docker.internal:27017"
                config = RunnableConfig(
                    configurable={"thread_id": st.session_state.current_chat_id}
                )
                with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
                    mongo_graph = graph_with_checkpointing(checkpointer)
                    for event in mongo_graph.stream(
                        state, config=config, stream_mode="values"
                    ):
                        if "messages" in event and event["messages"]:
                            last_message = event["messages"][-1]
                            if (
                                hasattr(last_message, "content")
                                and last_message.content
                            ):
                                full_response = last_message.content
                                response_container.markdown(
                                    f"""
                            <div class="assistant-message">
                                <strong>🤖 Assistant:</strong><br>
                                {full_response}
                            </div>
                            """,
                                    unsafe_allow_html=True,
                                )

                # Add assistant response to chat history
                if full_response:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )

            except Exception as e:
                error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

        # Save current chat
        save_current_chat()
        st.rerun()


if __name__ == "__main__":
    main()
