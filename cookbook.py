import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

# 1. Load environment variables from .env
load_dotenv()
api_key = os.getenv("x")

# Streamlit Page Configuration
st.set_page_config(
    page_title="Chef's Kitchen Assistant 🍳",
    page_icon="👨‍🍳",
    layout="centered",
)

# --- WARM COOKING APP CUSTOM CSS ---
st.markdown(
    """
    <style>
    /* Warm Kitchen Background */
    .stApp {
        background: linear-gradient(135deg, #fffcf5 0%, #f7f0e6 100%);
        color: #2c221e;
    }

    /* Culinary Header Banner */
    .recipe-header {
        background: linear-gradient(135deg, #e05638 0%, #d1492b 50%, #f4a261 100%);
        padding: 22px;
        border-radius: 18px;
        text-align: center;
        color: white;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 0.5px;
        box-shadow: 0 6px 20px rgba(224, 86, 56, 0.25);
        margin-bottom: 25px;
    }

    /* Sidebar - Soft Herbal/Olive Style */
    [data-testid="stSidebar"] {
        background: #f1f4ed;
        border-right: 1px solid #e1e7db;
    }

    /* User Chat Bubble (Terracotta / Warm Spice) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, #ffedd8 0%, #fcd5ce 100%);
        border-radius: 16px;
        padding: 12px;
        border: 1px solid #f8ad9d;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Assistant Chat Bubble (Herbal Mint / Kitchen Fresh) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 16px;
        padding: 12px;
        border: 1px solid #a5d6a7;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Text Color in Chat */
    [data-testid="stChatMessage"] p {
        color: #2b211b !important;
        font-size: 15px;
        line-height: 1.5;
    }

    /* Input Field Styling */
    .stChatInput input {
        background: #ffffff !important;
        border: 2px solid #e05638 !important;
        border-radius: 25px !important;
        color: #2b211b !important;
    }

    /* Buttons Styling */
    .stButton>button {
        background: linear-gradient(135deg, #e05638, #f4a261);
        color: white;
        border-radius: 20px;
        font-weight: bold;
        border: none;
        padding: 8px 18px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(224, 86, 56, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SYSTEM PROMPT (Cooking Assistant Persona) ---
COOKING_SYSTEM_PROMPT = """
You are 'Chef AI', an expert culinary assistant and friendly home-cooking coach.
Your behavior rules:
1. When the user asks for dish ideas or ingredients, give them clear recipe choices or list recipes one by one.
2. For each recipe, provide the dish name, prep time, cooking time, key ingredients list, and brief flavor profile.
3. Ask the user if they want to cook a specific dish.
4. When the user selects a dish to cook, guide them step-by-step through preparation and cooking.
5. Provide instructions ONE STEP AT A TIME. Wait for the user to confirm (e.g., 'next', 'done', 'ready') before moving to the next step.
6. Keep instructions practical, clear, encouraging, and include helpful cooking tips (e.g., pan temperature, knife safety, seasoning timing).
"""

# --- Sidebar Controls ---
with st.sidebar:
  st.markdown("### 🍳 Kitchen Controls")
  st.info(
      "💡 **How to use:**\n"
      "- Type what ingredients you have.\n"
      "- Pick a recipe from the list.\n"
      "- Ask to start cooking step-by-step!"
  )
  st.write("---")

  if st.button("🔄 Start New Recipe"):
    st.session_state.messages = [{
        "role": "system",
        "content": COOKING_SYSTEM_PROMPT,
    }]
    st.rerun()

  st.write("---")
  st.caption("Powered by Groq & OpenAI GPT-OSS 120B")

# --- Main App Header ---
st.markdown(
    '<div class="recipe-header">👨‍🍳 What Are We Cooking Today? 🥘</div>',
    unsafe_allow_html=True,
)

# Validate API key
if not api_key:
  st.error(
      "❌ **Error:** API key not found. Make sure variable `x` is defined in"
      " your `.env` file."
  )
  st.stop()

# Initialize Groq Client
client = Groq(api_key=api_key)
MODEL_NAME = "openai/gpt-oss-120b"

# Initialize Chat History
if "messages" not in st.session_state:
  st.session_state.messages = [
      {"role": "system", "content": COOKING_SYSTEM_PROMPT}
  ]

# Display Existing Chat Messages (skip system prompt)
for message in st.session_state.messages:
  if message["role"] != "system":
    avatar = "👨‍🍳" if message["role"] == "assistant" else "😋"
    with st.chat_message(message["role"], avatar=avatar):
      st.markdown(message["content"])

# --- User Input Handling ---
if user_input := st.chat_input("Ask for a recipe or tell me your ingredients..."):
  # Display user message
  with st.chat_message("user", avatar="😋"):
    st.markdown(user_input)

  st.session_state.messages.append({"role": "user", "content": user_input})

  # Generate Chef AI Response
  with st.chat_message("assistant", avatar="👨‍🍳"):
    with st.spinner("👨‍🍳 Preparing your recipe..."):
      try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            temperature=0.6,
            max_tokens=1024,
        )
        assistant_reply = response.choices[0].message.content
        st.markdown(assistant_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_reply}
        )

      except Exception as e:
        st.error(f"An error occurred: {e}")