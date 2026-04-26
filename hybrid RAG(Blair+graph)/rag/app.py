"""
Hybrid Retrieval System Frontend
Powered by Blair + Graph RAG
"""

import streamlit as st
from retriever import EnhancedHybridRetriever, Product
from response_generator2 import ResponseGenerator
from embedding_model import EmbeddingModel
import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Blair + Graph RAG",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .graph-insight {
        background: #e0f7fa;
        border-left: 3px solid #00bcd4;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #006064;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False
    st.session_state.conversation_history = []
    st.session_state.retriever = None
    st.session_state.embedding_model = None
    st.session_state.response_generator = None

# Initialize components
@st.cache_resource
def init_chatbot():
    retriever = EnhancedHybridRetriever(db_name=config.DB_NAME)
    embedding_model = EmbeddingModel(model_name=config.EMBEDDING_MODEL_NAME)
    response_generator = ResponseGenerator(model_name=config.RESPONSE_MODEL)
    return retriever, embedding_model, response_generator

# Sidebar
with st.sidebar:
    st.markdown("### 🕸️ Blair + Graph RAG")
    st.markdown("**Hybrid Search System**")
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. **Graph Filter**: Hard constraints (RAM, Price)
    2. **Vector Search**: Semantic matching
    3. **Graph Enrichment**: Sentiment insights
    """)
    
    if st.button("🔄 Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# Main content
st.markdown('<div class="main-header">Blair + Graph RAG System</div>', unsafe_allow_html=True)

if not st.session_state.chatbot_initialized:
    with st.spinner("Initializing System (Loading Models & Graph Connection)..."):
        try:
            retriever, embedding_model, response_generator = init_chatbot()
            st.session_state.retriever = retriever
            st.session_state.embedding_model = embedding_model
            st.session_state.response_generator = response_generator
            st.session_state.chatbot_initialized = True
            st.success("✅ System Ready!")
        except Exception as e:
            st.error(f"❌ Initialization error: {e}")
            st.stop()

# Chat Interface
for turn in st.session_state.conversation_history:
    with st.chat_message("user"):
        st.write(turn['user'])
    
    with st.chat_message("assistant"):
        st.write(turn['bot'])
        
        # Display Products
        if turn.get('products'):
            with st.expander(f"📦 View {len(turn['products'])} Recommended Products"):
                for p in turn['products']:
                    st.markdown(f"#### {p['title']}")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if p.get('image_url'):
                            st.image(p['image_url'], width=150)
                        st.markdown(f"**Price:** ${p['price']:.2f}" if p['price'] else "**Price:** N/A")
                        st.markdown(f"**Rating:** {p['rating']}★")
                    
                    with col2:
                        st.markdown(f"**ASIN:** `{p['asin']}`")
                        st.markdown(f"**Confidence:** {p['confidence_score']:.2%}")
                        
                        # Graph Insights
                        if p.get('graph_insights'):
                            st.markdown("**🕸️ Graph Sentiment Insights:**")
                            for feature, sentiment in p['graph_insights'].items():
                                st.markdown(f"<div class='graph-insight'><b>{feature}:</b> {sentiment}</div>", unsafe_allow_html=True)
                        
                        # Reviews
                        if p.get('relevant_reviews'):
                            st.markdown(f"**📝 Top Review:** *\"{p['relevant_reviews'][0]['title']}\"*")
                    
                    st.markdown("---")

# User Input
if prompt := st.chat_input("Ask about laptops (e.g., 'Cheap 16GB RAM laptop with good screen')"):
    st.session_state.conversation_history.append({'user': prompt, 'bot': '...', 'products': []})
    
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 2. Search (Hybrid)
            with st.status("🔍 **Hybrid Retrieval Process**", expanded=True) as status:
                st.write("1️⃣ Generating BLAIR Embeddings...")
                query_embedding = st.session_state.embedding_model.encode_query(prompt)
                
                st.write("2️⃣ Executing Graph + Vector Search...")
                products, search_log = st.session_state.retriever.search_unified(
                    query_embedding=query_embedding,
                    query_text=prompt,
                    top_products=10
                )
                
                # Display Search Log
                if search_log.get("constraints"):
                    st.info(f"🕸️ **Graph Filter**: Detected constraints: `{search_log['constraints']}`")
                    st.write(f"📉 Reduced search space to **{search_log['filtered_count']}** candidate products.")
                else:
                    st.write("ℹ️ No hard constraints detected. Performing full vector search.")
                
                st.write(f"✅ Found **{len(products)}** relevant products.")
                st.write(f"🧠 Enriched **{search_log.get('enrichment_count', 0)}** products with Sentiment Analysis.")
                
                status.update(label="✅ Retrieval Complete!", state="complete", expanded=False)
            
            # 3. Generate Response
            response = st.session_state.response_generator.generate_response(
                user_query=prompt,
                products=products,
                conversation_history=st.session_state.conversation_history[:-1]
            )
            
            st.write(response)
            
            # Update history
            st.session_state.conversation_history[-1]['bot'] = response
            st.session_state.conversation_history[-1]['products'] = [p.to_dict() for p in products]
            
            st.rerun()
