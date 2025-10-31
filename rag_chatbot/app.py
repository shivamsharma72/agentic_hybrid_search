"""
Streamlit Frontend for RAG E-commerce Chatbot
Beautiful UI for product search and recommendations
"""

import streamlit as st
from query_enhancer import QueryEnhancer
from hybrid_retriever import HybridRetriever, Product
from bm25_retriever import BM25Retriever
from response_generator import ResponseGenerator
import config

# Lazy import for embedding model to avoid startup issues
def get_embedding_model():
    """Lazy load embedding model"""
    from embedding_model import get_embedding_model as _get_model
    return _get_model()

# Page config
st.set_page_config(
    page_title="Electronics Shopping Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        color: #1a1a1a;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #0d47a1;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        color: #4a148c;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #1a1a1a;
    }
    .product-card h4 {
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False
    st.session_state.conversation_history = []
    st.session_state.query_enhancer = None
    st.session_state.semantic_retriever = None
    st.session_state.bm25_retriever = None
    st.session_state.response_generator = None
    st.session_state.search_mode = config.SEARCH_MODE  # Default from config

# Initialize chatbot components
@st.cache_resource
def init_chatbot():
    """Initialize chatbot components (cached)"""
    query_enhancer = QueryEnhancer(model_name=config.QUERY_ENHANCER_MODEL)
    semantic_retriever = HybridRetriever(db_name=config.DB_NAME)
    bm25_retriever = BM25Retriever(db_name=config.DB_NAME)
    response_generator = ResponseGenerator(model_name=config.RESPONSE_GENERATOR_MODEL)
    return query_enhancer, semantic_retriever, bm25_retriever, response_generator

# Sidebar
with st.sidebar:
    st.markdown("### 🛒 Electronics Shopping Assistant")
    st.markdown("---")
    
    st.markdown("**How to use:**")
    st.markdown("""
    - Ask for product recommendations
    - Specify budget, ratings, features
    - Get personalized suggestions
    """)
    
    st.markdown("---")
    st.markdown("**Example queries:**")
    st.code("🎮 Gaming laptop under $1000", language="text")
    st.code("🎧 Best wireless headphones", language="text")
    st.code("💡 I like Bose, suggest alternatives", language="text")
    st.code("📺 4K TV but not Samsung", language="text")
    
    st.markdown("---")
    st.markdown("**Settings:**")
    
    # Search mode selector
    search_mode = st.selectbox(
        "Search Mode",
        ["semantic", "bm25", "hybrid"],
        index=["semantic", "bm25", "hybrid"].index(st.session_state.search_mode),
        help="""
        • **Semantic**: AI-powered meaning-based search
        • **BM25**: Keyword-based search with brand intelligence
        • **Hybrid**: Best of both (recommended)
        """
    )
    
    # Update search mode if changed
    if search_mode != st.session_state.search_mode:
        st.session_state.search_mode = search_mode
        st.success(f"✅ Switched to {search_mode} mode")
    
    show_debug = st.checkbox("Show debug info", value=False)
    max_results = st.slider("Max results", 5, 20, config.MAX_RESULTS)
    
    st.markdown("---")
    
    # Stats
    if st.session_state.chatbot_initialized:
        st.markdown("**Session Stats:**")
        st.metric("Queries", len(st.session_state.conversation_history))
    
    st.markdown("---")
    
    if st.button("🔄 Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# Main content
st.markdown('<div class="main-header">🛒 Electronics Shopping Assistant</div>', unsafe_allow_html=True)
st.markdown("### Find the perfect electronics with AI-powered recommendations")

# Initialize chatbot
if not st.session_state.chatbot_initialized:
    with st.spinner("🤖 Initializing AI assistant..."):
        try:
            query_enhancer, semantic_retriever, bm25_retriever, response_generator = init_chatbot()
            st.session_state.query_enhancer = query_enhancer
            st.session_state.semantic_retriever = semantic_retriever
            st.session_state.bm25_retriever = bm25_retriever
            st.session_state.response_generator = response_generator
            
            # Load embedding model if vector search is enabled
            if config.USE_VECTOR_SEARCH:
                try:
                    st.session_state.embedding_model = get_embedding_model()
                    st.success("✅ Semantic search enabled!")
                except Exception as e:
                    st.warning(f"⚠️ Semantic search disabled: {e}")
                    st.session_state.embedding_model = None
            
            st.session_state.chatbot_initialized = True
            st.success(f"✅ Assistant ready! (Mode: {st.session_state.search_mode})")
        except Exception as e:
            st.error(f"❌ Initialization error: {e}")
            st.stop()

# Display conversation history
st.markdown("---")

if not st.session_state.conversation_history:
    st.info("👋 Hi! I'm your electronics shopping assistant. Ask me anything about products!")

for i, turn in enumerate(st.session_state.conversation_history):
    # User message
    with st.container():
        st.markdown(f"""
        <div class="chat-message user-message">
            <b>👤 You:</b><br>
            {turn['user']}
        </div>
        """, unsafe_allow_html=True)
    
    # Show products FIRST (top 3 with fixed-size images)
    if turn.get('products') and len(turn['products']) > 0:
        st.markdown(f"### 🛍️ Top Recommendations (Query {i+1})")
        cols = st.columns(3)
        for idx, product_dict in enumerate(turn['products'][:3]):
            with cols[idx]:
                # Display image
                if product_dict.get('image_url'):
                    try:
                        st.image(product_dict['image_url'], width=200, use_container_width=False, caption="")
                    except Exception as e:
                        st.info("📷 Image unavailable")
                else:
                    st.info("📷 No image")
                
                # Product info
                st.markdown(f"**{product_dict['title'][:60]}...**")
                
                price = f"${product_dict['price']:.2f}" if product_dict.get('price') else "N/A"
                rating = f"{product_dict['rating']:.1f}★" if product_dict.get('rating') else "N/A"
                
                st.markdown(f"💰 **{price}**")
                st.markdown(f"⭐ **{rating}** ({product_dict.get('num_reviews', 0):,} reviews)")
                st.markdown(f"🔖 **ASIN:** `{product_dict['asin']}`")
        
        st.markdown("---")
    
    # THEN show bot explanation text
    with st.container():
        st.markdown(f"""
        <div class="chat-message bot-message">
            <b>🤖 Assistant's Analysis:</b><br>
            {turn['bot']}
        </div>
        """, unsafe_allow_html=True)
    
    # Show products if available
    if turn.get('products'):
        with st.expander(f"📦 View {len(turn['products'])} Products"):
            cols = st.columns(2)
            for idx, product_dict in enumerate(turn['products'][:6]):  # Show top 6
                col = cols[idx % 2]
                with col:
                    # Product is now a dict
                    price_str = f"${product_dict['price']:.2f}" if product_dict.get('price') else "N/A"
                    rating_str = f"{product_dict['rating']:.1f}★" if product_dict.get('rating') else "N/A"
                    
                    # Show image if available
                    if product_dict.get('image_url'):
                        try:
                            st.image(product_dict['image_url'], width=200, caption=product_dict['title'][:40])
                        except Exception as e:
                            st.warning(f"⚠️ Image failed to load")
                    else:
                        st.info("📷 No image available")
                    
                    st.markdown(f"""
                    <div class="product-card">
                        <h4>{product_dict['title'][:60]}...</h4>
                        <p><b>💰 Price:</b> {price_str}</p>
                        <p><b>⭐ Rating:</b> {rating_str} ({product_dict.get('num_reviews', 0):,} reviews)</p>
                        <p><b>📂 Category:</b> {product_dict.get('category', 'N/A')}</p>
                        <p><b>🔗 ASIN:</b> <code>{product_dict['asin']}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Show debug info
    if show_debug and turn.get('enhanced_query'):
        with st.expander("🔍 Debug Info"):
            st.json(turn['enhanced_query'])

# Chat input
st.markdown("---")

# Use form for better UX
with st.form(key='chat_form', clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask me anything:",
            placeholder="e.g., I need a gaming laptop under $1000",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 🚀")

# Process user input
if submit_button and user_input:
    with st.spinner("🔍 Searching..."):
        try:
            # Step 1: Enhance query
            enhanced = st.session_state.query_enhancer.enhance_query(user_input)
            
            if show_debug:
                st.info(f"🧠 **Extracted Query:**\n- Keywords: {enhanced.keywords}\n- Category: {enhanced.main_category}\n- Price: ${enhanced.price_min or 0} - ${enhanced.price_max or '∞'}\n- Min Rating: {enhanced.min_rating or 'Any'}\n- Intent: {enhanced.intent}")
            
            # Step 2: Retrieve products based on search mode
            if st.session_state.search_mode == "bm25":
                # BM25 keyword search only
                products_list = st.session_state.bm25_retriever.search_bm25(
                    query=user_input,
                    category=enhanced.main_category,
                    price_min=enhanced.price_min,
                    price_max=enhanced.price_max,
                    min_rating=enhanced.min_rating,
                    limit=max_results
                )
                # Convert dicts to Product objects
                products = [
                    Product(
                        asin=p['asin'],
                        title=p['title'],
                        price=p['price'],
                        rating=p['rating'],
                        num_reviews=p['num_reviews'],
                        category=p['category'],
                        similarity=p['similarity'],
                        image_url=p['image_url']
                    )
                    for p in products_list
                ]
                
            elif st.session_state.search_mode == "semantic":
                # Semantic vector search only
                query_embedding = None
                use_vector = config.USE_VECTOR_SEARCH and st.session_state.get('embedding_model') is not None
                if use_vector:
                    query_text = " ".join(enhanced.keywords)
                    query_embedding = st.session_state.embedding_model.encode_query(query_text)
                
                products = st.session_state.semantic_retriever.search(
                    keywords=enhanced.keywords,
                    category=enhanced.main_category,
                    price_min=enhanced.price_min,
                    price_max=enhanced.price_max,
                    min_rating=enhanced.min_rating,
                    sort_by=enhanced.sort_by or "rating_number",
                    limit=max_results,
                    use_vector=use_vector,
                    query_embedding=query_embedding
                )
            
            else:  # hybrid mode
                # Run both searches and merge
                # BM25 results
                bm25_results = st.session_state.bm25_retriever.search_bm25(
                    query=user_input,
                    category=enhanced.main_category,
                    price_min=enhanced.price_min,
                    price_max=enhanced.price_max,
                    min_rating=enhanced.min_rating,
                    limit=max_results // 2
                )
                
                # Semantic results
                query_embedding = None
                use_vector = config.USE_VECTOR_SEARCH and st.session_state.get('embedding_model') is not None
                if use_vector:
                    query_text = " ".join(enhanced.keywords)
                    query_embedding = st.session_state.embedding_model.encode_query(query_text)
                
                semantic_results = st.session_state.semantic_retriever.search(
                    keywords=enhanced.keywords,
                    category=enhanced.main_category,
                    price_min=enhanced.price_min,
                    price_max=enhanced.price_max,
                    min_rating=enhanced.min_rating,
                    sort_by=enhanced.sort_by or "rating_number",
                    limit=max_results // 2,
                    use_vector=use_vector,
                    query_embedding=query_embedding
                )
                
                # Merge and deduplicate
                products_dict = {}
                # Add BM25 results
                for p in bm25_results:
                    products_dict[p['asin']] = Product(
                        asin=p['asin'],
                        title=p['title'],
                        price=p['price'],
                        rating=p['rating'],
                        num_reviews=p['num_reviews'],
                        category=p['category'],
                        similarity=p['similarity'],
                        image_url=p['image_url']
                    )
                
                # Add semantic results
                for p in semantic_results:
                    if p.asin not in products_dict:
                        products_dict[p.asin] = p
                    else:
                        # Boost if appears in both
                        products_dict[p.asin].similarity = (
                            products_dict[p.asin].similarity + (p.similarity or 0)
                        ) / 2
                
                products = list(products_dict.values())
                # Sort by combined score
                products.sort(key=lambda p: (p.similarity or 0, p.num_reviews or 0), reverse=True)
                products = products[:max_results]
            
            # Step 2.5: Get reviews for top products
            product_asins = [p.asin for p in products[:5]]  # Get reviews for top 5
            reviews_by_product = st.session_state.semantic_retriever.get_reviews_for_products(product_asins, limit_per_product=3)
            
            if show_debug:
                debug_info = f"🔍 **Found {len(products)} products**\n\n"
                debug_info += "**Top 3 Products:**\n"
                for i, p in enumerate(products[:3], 1):
                    debug_info += f"{i}. **{p.title[:50]}...** (ASIN: {p.asin})\n"
                    debug_info += f"   - Price: ${p.price if p.price else 'N/A'}\n"
                    debug_info += f"   - Image: {'✅ Yes' if p.image_url else '❌ No'}\n"
                st.info(debug_info)
            
            # Step 3: Generate response with reviews
            response = st.session_state.response_generator.generate_response(
                user_query=user_input,
                products=products,
                reviews_by_product=reviews_by_product,
                enhanced_query=enhanced.model_dump(),
                conversation_history=st.session_state.conversation_history
            )
            
            # Add to conversation history (convert products to dicts for session state)
            st.session_state.conversation_history.append({
                'user': user_input,
                'bot': response,
                'products': [p.to_dict() for p in products],  # Convert to dict
                'enhanced_query': enhanced.model_dump()
            })
            
            # Rerun to show new message
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            if show_debug:
                st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 Powered by OpenAI GPT-3.5 + LangChain + PostgreSQL</p>
    <p>📊 348,228 Electronics Products | 35 Categories</p>
</div>
""", unsafe_allow_html=True)

