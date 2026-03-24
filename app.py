import streamlit as st
import requests
from streamlit_agraph import agraph, Node, Edge, Config

# 1. Global Page Configuration
st.set_page_config(page_title="Synapse | Intelligence Dashboard", page_icon="🧠", layout="wide")

# 2. Professional "Linear-style" Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    /* Formal Button Styling */
    div.stButton > button:first-child {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #4f46e5;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    /* Professional Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; color: #F0F6FC; }
    .stMarkdown { color: #C9D1D9; }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialize Session State (For Chat & Dynamic Graph)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "graph_nodes" not in st.session_state:
    # Seed nodes for the demo start
    st.session_state.graph_nodes = [
        Node(id="UPSC", label="UPSC 2026", size=25, color="#6366F1"),
        Node(id="IFoS", label="IFoS Prep", size=25, color="#10B981")
    ]
if "graph_edges" not in st.session_state:
    st.session_state.graph_edges = [Edge(source="UPSC", target="IFoS", label="Core Link", color="#334155")]

# 4. Sidebar: Data Ingestion & Stats
with st.sidebar:
    st.title("Synapse")
    st.caption("Agentic Knowledge Management v1.0")
    st.divider()
    
    st.subheader("📥 Data Ingestion")
    topic = st.text_input("Syllabus Topic", placeholder="e.g. Indian Forest Act")
    content = st.text_area("Detailed Notes", placeholder="Paste study material here...", height=150)
    
    if st.button("Assimilate Memory ⚡", use_container_width=True):
        if topic and content:
            with st.spinner("Rewiring neural pathways..."):
                try:
                    res = requests.post("http://127.0.0.1:8000/memorize/", json={"topic": topic, "content": content})
                    if res.status_code == 200:
                        st.toast(f"Memory Encoded: {topic}", icon="✅")
                        st.balloons()
                        # DYNAMIC GRAPH UPDATE: Add the new topic as a node
                        if topic not in [n.id for n in st.session_state.graph_nodes]:
                            new_node = Node(id=topic, label=topic, size=20, color="#818CF8")
                            st.session_state.graph_nodes.append(new_node)
                            # Link it to the last added node to show "Connection"
                            if len(st.session_state.graph_nodes) > 1:
                                prev_node = st.session_state.graph_nodes[-2].id
                                st.session_state.graph_edges.append(Edge(source=prev_node, target=topic, color="#334155"))
                    else:
                        st.error("Backend Error. Check main.py.")
                except:
                    st.error("Connection Failed. Is the backend running?")
        else:
            st.warning("Input required.")

    st.divider()
    st.subheader("📈 System Health")
    c1, c2 = st.columns(2)
    c1.metric("Nodes", len(st.session_state.graph_nodes), "4")
    c2.metric("Decay", "3%", "-1.2%", delta_color="inverse")

# 5. Main Dashboard Layout
st.title("Synapse 🧠")
st.markdown("Connecting interdisciplinary concepts for long-term mastery.")
st.divider()

col_chat, col_graph = st.columns([1.2, 1])

# --- LEFT COLUMN: Neural Retrieval (Chat) ---
with col_chat:
    st.subheader("🔍 Neural Retrieval")
    
    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧠" if message["role"]=="assistant" else None):
            st.markdown(message["content"])

    # Chat Input & Logic
    if prompt := st.chat_input("Query your 2.5-year memory..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Searching graph..."):
            try:
                res = requests.post("http://127.0.0.1:8000/recall/", json={"question": prompt})
                if res.status_code == 200:
                    data = res.json()
                    memories = data.get("answer", [])

                    if memories:
                        # Extracting the actual content from Membrain's response
                        source_text = memories[0].get("source", {}).get("content", "Memory found, but text is unreachable.")
                        ai_reply = f"**Based on your notes:**\n\n> {source_text}"
                    else:
                        ai_reply = "I don't have a specific memory for that yet. Have you assimilated those notes?"

                    with st.chat_message("assistant", avatar="🧠"):
                        st.markdown(ai_reply)
                        with st.expander("View Semantic Metadata"):
                            st.json(data)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                else:
                    st.error("Retrieval failed.")
            except:
                st.error("Backend unreachable.")

# --- RIGHT COLUMN: Semantic Map (Live Graph) ---
with col_graph:
    st.subheader("🕸️ Semantic Map")
    st.caption("Real-time knowledge relationship visualization")
    
    graph_config = Config(
        width=550, height=500, directed=True, physics=True, 
        nodeHighlightBehavior=True, highlightColor="#FDE047",
        collapsible=False, staticGraph=False
    )

    agraph(nodes=st.session_state.graph_nodes, 
           edges=st.session_state.graph_edges, 
           config=graph_config)