import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a, #1e293b); }

/* make all text visible on the dark background */
.stApp, .stApp p, .stApp li, .stApp span, .stApp label,
[data-testid="stChatMessage"] *,
[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
[data-testid="stSidebar"] { background: #0b1220; }

.hero {
    text-align: center; padding: 20px; border-radius: 16px;
    background: linear-gradient(90deg, #6366f1, #ec4899);
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.hero h1 { margin: 0; font-size: 2rem; color: white !important; }
.hero p  { margin: 4px 0 0; opacity: 0.9; color: white !important; }

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.06);
    border-radius: 14px; padding: 12px; margin-bottom: 10px;
}
[data-testid="stChatInput"] textarea {
    border-radius: 12px;
    background: #ffffff !important;
    color: #0f172a !important;
}
.footer { text-align: center; font-size: 0.8rem; margin-top: 30px; color: #94a3b8 !important; }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- HTML header ----------
st.markdown("""
<div class="hero">
    <h1>🤖 AI Chatbot</h1>
    <p>GPT-OSS + LangChain ConversationBufferMemory</p>
</div>
""", unsafe_allow_html=True)

# ---------- LLM ----------
llm = ChatGroq(
    model="openai/gpt-oss-120b",   # or "openai/gpt-oss-20b" (faster)
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=0.7,
)

# ---------- Prompt ----------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, friendly assistant. Keep answers short and clear."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
chain = prompt | llm

# ---------- Memory (ConversationBufferMemory) ----------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="history",
    )
memory = st.session_state.memory

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Options")
    if st.button("🗑️ Clear chat"):
        memory.clear()
        st.rerun()
    st.caption(f"Messages in memory: {len(memory.chat_memory.messages)}")

# ---------- Show chat ----------
for m in memory.chat_memory.messages:
    role = "user" if m.type == "human" else "assistant"
    st.chat_message(role).write(m.content)

# ---------- Chat input ----------
if user_input := st.chat_input("Say something..."):
    st.chat_message("user").write(user_input)

    history = memory.load_memory_variables({})["history"]   # read memory

    with st.chat_message("assistant"):
        reply = st.write_stream(
            c.content for c in chain.stream({
                "history": history,
                "input": user_input,
            })
        )

    memory.save_context({"input": user_input}, {"output": reply})  # write memory

st.markdown('<div class="footer">Built by Mythili • Python • LangChain • Groq</div>',
            unsafe_allow_html=True)