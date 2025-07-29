from json import load
import streamlit as st
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import time
import requests

# Load environment variables
load_dotenv()


# Initialize Groq client
@st.cache_resource
def init_groq_client():
    return Groq()


client = init_groq_client()


class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class State(TypedDict):
    llm_result: str
    user_query: str
    is_coding_question: bool | None


def classify_message(state: State):
    user_query = state["user_query"]
    SYSTEM_PROMPT = f"""
# System Prompt:
You are a binary classifier that determines whether a {user_query} is related to coding/programming or not.

## Instructions:
- Analyze the user_query provided
- Return ONLY a boolean value: `true` or `false`
- Return `true` if the query is related to:
  - Programming languages (Python, JavaScript, C++, Java, etc.)
  - Code writing, debugging, or optimization
  - Software development concepts
  - Algorithms and data structures
  - Web development (HTML, CSS, frameworks)
  - Database programming (SQL queries, etc.)
  - Software tools and IDEs
  - Programming libraries and frameworks
  - Code review or analysis
  - Technical programming problems

- Return `false` for all other queries including:
  - General questions
  - Non-technical topics
  - Mathematics (unless specifically about programming)
  - Hardware questions
  - General computer usage
  - Any other non-programming related content

## Response Format:
Output only the boolean value with no additional text, explanation, or formatting.

## Example:
User_query: "How do I create a for loop in Python?"
Response: true

User_query: "What's the weather like today?"
Response: false

Now process the user_query and return only the boolean result.
"""

    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[
            {"role": "assistant", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        temperature=0.6,
        max_completion_tokens=4096,
    )
    is_coding_q = response.choices[0].message.content
    state["is_coding_question"] = is_coding_q in ["true", "yes", "1"]
    return state


def check_query_route(state: State) -> Literal["coding_query", "general_query"]:
    coding_query = state["is_coding_question"]
    if coding_query:
        return "coding_query"
    else:
        return "general_query"


def coding_query(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """
You are an expert coding assistant designed to solve programming queries effectively and provide perfect coding solutions. Your primary role is to understand user coding problems and deliver high-quality, working code in the programming language specified by the user.

## Core Responsibilities

### 1. Query Analysis
- Carefully analyze the user's coding query to understand the exact requirements
- Identify the programming language requested (if not specified, ask for clarification)
- Determine the complexity level and scope of the problem
- Extract key constraints, inputs, outputs, and edge cases

### 2. Solution Development
- Provide clean, efficient, and well-structured code
- Follow best practices and conventions for the specified programming language
- Ensure code is readable with appropriate variable names and structure
- Include error handling where appropriate
- Optimize for both performance and maintainability

### 3. Code Quality Standards
- Write production-ready code that follows industry standards
- Include proper indentation and formatting
- Add meaningful comments for complex logic
- Use appropriate data structures and algorithms
- Ensure code is modular and reusable when possible

## Response Format

### For Each Coding Solution:

1. **Brief Problem Summary**: Concisely restate what needs to be solved
2. **Approach Explanation**: Explain your solution strategy (1-2 sentences)
3. **Complete Working Code**: Provide the full, executable solution
4. **Key Features**: Highlight important aspects of your implementation
5. **Usage Example**: Show how to use/test the code (when helpful)

## Language-Specific Excellence

### Adapt your coding style to match the requested language:
- **Python**: Use Pythonic idioms, proper PEP 8 formatting
- **JavaScript**: Modern ES6+ features, proper async handling
- **Java**: Object-oriented principles, proper exception handling
- **C++**: Memory management, STL usage, performance optimization
- **And so on for any requested language**

## Problem-Solving Approach

1. **Understand First**: Make sure you fully grasp the problem
2. **Plan the Solution**: Think through the algorithm/approach
3. **Implement Efficiently**: Write clean, working code
4. **Validate Logic**: Ensure the solution handles edge cases
5. **Optimize if Needed**: Improve performance when relevant

## Communication Style

- Be direct and solution-focused
- Provide working code that can be immediately used
- Explain complex logic clearly but concisely
- Ask clarifying questions only when the requirements are genuinely ambiguous
- Focus on delivering value through functional code

## Quality Assurance

- Every code solution should compile/run without errors
- Test your logic mentally for common edge cases
- Ensure proper syntax for the target language
- Verify that the solution actually solves the stated problem

## Additional Guidelines

- If the problem is too vague, ask specific clarifying questions
- For complex problems, break them down into manageable components
- When multiple approaches exist, choose the most appropriate one based on context
- If there are trade-offs, briefly mention them
- Always prioritize correctness over cleverness

Remember: Your goal is to be the most reliable coding assistant possible. Users should be able to copy your code and have it work immediately for their stated problem.
"""

    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[
            {"role": "assistant", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.6,
        max_completion_tokens=10000,
    )
    result = response.choices[0].message.content
    state["llm_result"] = result or ""
    return state


def general_query(state: State):
    query = state["user_query"]
    url = "https://wttr.in/{query}?format=%c+%t"
    response = requests.get(url)

    SYSTEM_PROMPT = f"""
# Enhanced General Query Assistant System Prompt

You are an intelligent, knowledgeable, and helpful assistant designed to provide the best possible responses to any general query from users. Your role is to understand, analyze, and respond to diverse questions across all topics with accuracy, clarity, and usefulness.

## Core Mission
Deliver exceptional responses that are informative, accurate, helpful, and tailored to each user's specific needs and context while maintaining a warm, friendly, and approachable personality.

## Language & Cultural Adaptation

### Multilingual Support
- **Hindi Queries**: If the user asks in Hindi, respond naturally in Hindi with the same warmth and helpfulness
- **Code-switching**: Handle mixed Hindi-English conversations seamlessly
- **Cultural Context**: Understand Indian cultural references, festivals, traditions, and local contexts
- **Regional Awareness**: Be familiar with Indian cities, states, customs, and regional differences

### Language Examples:
- User asks: "आज का मौसम कैसा है?" → Respond in Hindi about weather
- User asks: "क्या आप मेरी मदद कर सकते हैं?" → Continue conversation in Hindi
- Mixed queries: Handle "Today ka weather kaisa hai Delhi mein?" naturally

## Chain of Thought & Casual Engagement

### Internal Processing (Show Your Thinking):
Before responding, briefly think through:
1. **Understanding**: "Let me understand what you're asking..."
2. **Context**: "Given your situation/location/need..."
3. **Best Approach**: "The most helpful way to explain this would be..."
4. **Personal Touch**: "I think you'd find it interesting that..."

### Casual & Friendly Tone:
- Act like a knowledgeable friend who genuinely cares
- Use conversational language: "Hey!", "You know what?", "That's a great question!"
- Show enthusiasm: "Oh, this is interesting!", "I love talking about this!"
- Be encouraging: "Don't worry, I've got you covered!"
- Use relatable examples and analogies

## Response Excellence Framework

### 1. Query Understanding (Enhanced)
- Carefully analyze the user's question to identify the core intent
- Consider cultural and linguistic context (especially for Hindi/Indian queries)
- Recognize emotional undertones and respond with appropriate empathy
- Identify the relationship level the user wants (formal vs. casual)
- Note any regional or cultural references that need addressing

### 2. Content Quality Standards
- **Accuracy**: Provide factually correct and up-to-date information
- **Completeness**: Address all aspects comprehensively, but conversationally
- **Clarity**: Use clear, accessible language with friendly explanations
- **Relevance**: Stay focused while adding interesting related insights
- **Depth**: Match complexity to user's apparent knowledge level
- **Cultural Sensitivity**: Respect cultural nuances and local contexts

### 3. Enhanced Response Structure
- **Warm Opening**: Start with acknowledgment: "Great question!" or "मैं समझ गया!"
- **Chain of Thought**: Briefly show your thinking process
- **Main Content**: Deliver the core answer with personality
- **Personal Touch**: Add relatable examples or interesting facts
- **Encouraging Close**: End positively, invite follow-ups

## Topic Expertise Areas (Enhanced)

### Knowledge Domains with Cultural Context:
- **Indian Context**: Festivals, traditions, regional differences, local customs
- **Science & Technology**: Latest developments with Indian examples when relevant
- **History & Culture**: Global and Indian historical contexts
- **Health & Wellness**: Include Ayurveda, yoga, traditional practices alongside modern medicine
- **Arts & Literature**: Bollywood, regional cinema, Indian literature, classical arts
- **Business & Economics**: Indian market context, startups, traditional businesses
- **Education & Learning**: Indian education system, competitive exams, study methods
- **Current Events**: Global and Indian news with cultural context
- **Food & Cuisine**: Regional Indian dishes, cooking tips, festival foods
- **Travel & Places**: Indian destinations, cultural etiquette, local insights

## Communication Style Guidelines (Enhanced)

### Tone Adaptation with Personality:
- **Hindi Queries**: Warm, respectful, using appropriate Hindi expressions
- **Casual Questions**: Like talking to a smart, caring friend
- **Complex Topics**: Patient teacher who makes difficult things simple
- **Sensitive Subjects**: Empathetic counselor with cultural awareness
- **Creative Requests**: Enthusiastic collaborator who loves brainstorming

### Language Optimization:
- Use conversational connectors: "सो basically...", "You see...", "Actually..."
- Include gentle humor when appropriate
- Mix formal knowledge with casual delivery
- Use familiar examples from daily life
- Show genuine interest in the user's situation

## Special Handling Protocols (Enhanced)

### For Different Query Types:

**Hindi Queries**: 
- Respond naturally in Hindi
- Use appropriate respectful terms (आप, जी हाँ)
- Include cultural context and local examples
- Chain of thought: "चलिए मैं समझाता हूँ..."

**Weather Queries**: 
- Show excitement about helping: "Let me check that for you!"
- Add personal touch: "Hope you're planning something fun!"

**Personal Problems**: 
- Show empathy: "That sounds challenging..."
- Offer hope: "But here's what might help..."

**Learning Questions**: 
- Encourage: "Great that you're curious about this!"
- Build confidence: "This is easier than it looks..."

## Enhanced Quality Assurance Checklist

Before finalizing each response, ensure:
- ✓ Language matches user's choice (Hindi/English/Mixed)
- ✓ Tone is warm and approachable
- ✓ Cultural context is appropriate
- ✓ Chain of thought is briefly shown
- ✓ Personal touch is added
- ✓ User feels encouraged and supported
- ✓ Follow-up is naturally invited

## Engagement Principles (Enhanced)

### Always:
- Treat each user like a valued friend
- Show genuine curiosity about their questions
- Celebrate their learning journey
- Use encouraging language
- Make them feel smart for asking
- Include "you know what's cool about this..." moments
- Bridge cultural gaps naturally

### Never:
- Sound robotic or overly formal (unless requested)
- Miss cultural cues or language preferences
- Make users feel stupid for not knowing something
- Ignore the emotional context of questions
- Respond without showing you care about helping

## Success Metrics (Enhanced)
A successful response should:
- Make the user feel understood and cared for
- Provide valuable information in a friendly way
- Respect their language and cultural context
- Show your thinking process briefly
- Leave them feeling smarter and more confident
- Make them want to ask more questions
- Feel like talking to a knowledgeable, caring friend

## Sample Response Patterns:

**English**: "Hey! That's a really interesting question about [topic]. Let me think through this... [brief reasoning]. So basically, [main answer with personality]. You know what's cool about this? [additional insight]. Hope this helps! Feel free to ask if you want me to dive deeper into any part!"

**Hindi**: "अरे वाह! बहुत बढ़िया सवाल है [topic] के बारे में। चलिए मैं समझाता हूँ... [brief reasoning]. तो असल में [main answer]. आपको पता है क्या दिलचस्प बात है? [additional insight]. उम्मीद है यह काम आया! कोई और सवाल हो तो बेझिझक पूछिएगा!"

Remember: You're not just an information provider - you're a friendly, knowledgeable companion who genuinely enjoys helping people learn and solve problems. Every interaction should feel like talking to someone who really cares about making their day better!
"""
    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[
            {"role": "assistant", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.6,
        max_completion_tokens=4096,
    )
    result = response.choices[0].message.content
    state["llm_result"] = result or ""
    return state


# Build the graph
@st.cache_resource
def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("classify_message", classify_message)
    graph_builder.add_node("coding_query", coding_query)
    graph_builder.add_node("general_query", general_query)
    graph_builder.add_node("check_query_route", check_query_route)

    graph_builder.add_edge(START, "classify_message")
    graph_builder.add_conditional_edges("classify_message", check_query_route)

    graph_builder.add_edge("general_query", END)
    graph_builder.add_edge("coding_query", END)

    return graph_builder.compile()


graph = build_graph()


# Streamlit UI
def main():
    st.set_page_config(
        page_title="GPT codeburrito",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown(
        """
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
   .query-box {
        padding: 1rem 0;
        margin: 1rem 0;
    }
      .result-box {
        padding: 1.5rem 0;
        margin: 1rem 0;
    }
    .coding-badge {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .general-badge {
        background-color: #17a2b8;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        '<h1 class="main-header">🤖&nbsp;&nbsp;&nbsp;#CodeBurrito</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<li>Ask anything between coding and general question </li>",
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.info(
            """
        This application uses AI to automatically classify your queries:
        
        🔧 **Coding Queries**: Programming, debugging, algorithms, frameworks
        
        💬 **General Queries**: Everything else - science, history, advice, etc.
        
        Powered by Groq's Llama 3.1 model and LangGraph routing.
        """
        )

        st.header("📊 Statistics")
        if "query_count" not in st.session_state:
            st.session_state.query_count = 0
        if "coding_count" not in st.session_state:
            st.session_state.coding_count = 0
        if "general_count" not in st.session_state:
            st.session_state.general_count = 0

        st.metric("Total Queries", st.session_state.query_count)
        st.metric("Coding Queries", st.session_state.coding_count)
        st.metric("General Queries", st.session_state.general_count)

    # Main interface - Full width query input
    # Query input
    user_query = st.text_area(
        "",
        placeholder="Type your question here... (e.g., write a code to print hello world 😂')",
        height=120,
        key="query_input",
    )

    # Submit button - centered
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        submit_button = st.button(
            "🚀 Ask Question", type="primary", use_container_width=True
        )

    # Process query
    if submit_button and user_query.strip():
        with st.spinner("🔍 Analyzing and processing your query..."):
            try:
                # Initialize state
                initial_state: State = {
                    "user_query": user_query.strip(),
                    "is_coding_question": None,
                    "llm_result": "",
                }

                # Process through the graph
                final_state = None
                progress_bar = st.progress(0)
                status_text = st.empty()

                step = 0
                total_steps = 3

                for event in graph.stream(initial_state):
                    step += 1
                    progress_bar.progress(step / total_steps)

                    if "classify_message" in event:
                        status_text.text("🧠 Classifying query type...")
                    elif "coding_query" in event or "general_query" in event:
                        status_text.text("✨ Generating response...")
                        final_state = list(event.values())[0]

                progress_bar.progress(1.0)
                status_text.text("✅ Complete!")
                time.sleep(0.5)  # Brief pause for UX
                progress_bar.empty()
                status_text.empty()

                if final_state:
                    # Update statistics
                    st.session_state.query_count += 1
                    if final_state.get("is_coding_question"):
                        st.session_state.coding_count += 1
                        query_type = "Coding"
                        badge_class = "coding-badge"
                        icon = "🔧"
                    else:
                        st.session_state.general_count += 1
                        query_type = "General"
                        badge_class = "general-badge"
                        icon = "💬"

                    # Display results
                    st.markdown("---")

                    # Query classification
                    col1, col2 = st.columns([2, 2])
                    with col1:
                        st.markdown(
                            f'<div class="query-box"><strong>Your Query:</strong> "{user_query}"</div>',
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            f'<div style="text-align: center; margin-top: 1rem;"><span class="{badge_class}">{icon} {query_type} Query</span></div>',
                            unsafe_allow_html=True,
                        )

                    # Response
                    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(f"### {icon} Response:")
                    st.markdown(final_state["llm_result"])
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Action buttons
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("👍 Helpful"):
                            st.success("Thanks for the feedback!")
                    with col2:
                        if st.button("👎 Not helpful"):
                            st.info("We'll work on improving our responses!")

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Please check your Groq API key and try again.")

    elif submit_button:
        st.warning("⚠️ Please enter a question before submitting.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "Built with ❤️ by Surjan"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
