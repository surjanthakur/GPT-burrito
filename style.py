import streamlit as st


def Page_styling():
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
