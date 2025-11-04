"""
Enhanced Streamlit Frontend with BLAIR Cross-Modal Search
Beautiful UI for product search with review evidence
"""

import streamlit as st
from retriever import EnhancedHybridRetriever, Product
from response_generator import ResponseGenerator
from embedding_model import EmbeddingModel
import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="🧠 Enhanced Electronics Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (enhanced)
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
    .review-evidence {
        background: #fffde7;
        border-left: 3px solid #fbc02d;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .high-confidence {
        background: #c8e6c9;
        color: #2e7d32;
    }
    .medium-confidence {
        background: #fff9c4;
        color: #f57f17;
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
    st.session_state.retriever = None
    st.session_state.embedding_model = None
    st.session_state.response_generator = None
    st.session_state.search_strategy = "balanced"  # Default strategy

# Initialize chatbot components
@st.cache_resource
def init_chatbot():
    """Initialize chatbot components (cached)"""
    retriever = EnhancedHybridRetriever(db_name=config.DB_NAME)
    embedding_model = EmbeddingModel(model_name=config.EMBEDDING_MODEL_NAME)
    response_generator = ResponseGenerator(model_name=config.RESPONSE_MODEL)
    return retriever, embedding_model, response_generator

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 Enhanced Shopping Assistant")
    st.markdown("**Powered by BLAIR Cross-Modal Embeddings**")
    st.markdown("---")
    
    st.markdown("**✨ What's New:**")
    st.markdown("""
    - 🔍 Searches products **AND** reviews
    - 💬 Uses review evidence for confidence
    - 🎯 Discovers products via mentions
    - 📊 BLAIR aligns products with reviews
    """)
    
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("""
    - Ask about product experiences
    - Mention quality or user feedback
    - Get evidence-based recommendations
    """)
    
    st.markdown("---")
    st.markdown("**Example queries:**")
    st.code("🤫 Quiet laptop for office", language="text")
    st.code("💪 Durable laptop for students", language="text")
    st.code("🌞 Bright screen for outdoor use", language="text")
    st.code("⌨️ Comfortable keyboard for writing", language="text")
    
    st.markdown("---")
    st.markdown("**Settings:**")
    
    # Search strategy selector
    search_strategy = st.selectbox(
        "Search Strategy",
        ["balanced", "product_focused", "review_focused"],
        index=["balanced", "product_focused", "review_focused"].index(st.session_state.search_strategy),
        help="""
        • **Balanced**: Equal weight to products & reviews (20+50)
        • **Product-focused**: Prioritize product matches (20+30)
        • **Review-focused**: Discover via review mentions (15+60)
        """
    )
    
    # Update strategy if changed
    if search_strategy != st.session_state.search_strategy:
        st.session_state.search_strategy = search_strategy
        st.success(f"✅ Switched to '{search_strategy}' strategy")
    
    show_review_evidence = st.checkbox("Show review evidence", value=True)
    show_debug = st.checkbox("Show debug info", value=False)
    max_results = st.slider("Max results", 5, 15, 10)
    
    st.markdown("---")
    
    # Stats
    if st.session_state.chatbot_initialized:
        st.markdown("**Session Stats:**")
        st.metric("Queries", len(st.session_state.conversation_history))
    
    st.markdown("---")
    
    if st.button("🔄 Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🤖 Powered by OpenAI GPT-3.5 + BLAIR-RoBERTa</p>
        <p>💻 5,455 Laptops | 350K Reviews</p>
        <p>🧠 Cross-Modal Embeddings</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-header">🧠 Enhanced Electronics Assistant</div>', unsafe_allow_html=True)
st.markdown("### AI-powered recommendations with review evidence")

# Initialize chatbot
if not st.session_state.chatbot_initialized:
    with st.spinner("🤖 Initializing AI assistant..."):
        try:
            retriever, embedding_model, response_generator = init_chatbot()
            st.session_state.retriever = retriever
            st.session_state.embedding_model = embedding_model
            st.session_state.response_generator = response_generator
            
            st.session_state.chatbot_initialized = True
            st.success(f"✅ Assistant ready! (Strategy: {st.session_state.search_strategy})")
        except Exception as e:
            st.error(f"❌ Initialization error: {e}")
            st.stop()

# Display conversation history
st.markdown("---")

if not st.session_state.conversation_history:
    st.info("👋 Hi! I'm your enhanced electronics assistant. I search products AND reviews to find the best matches with evidence!")

for i, turn in enumerate(st.session_state.conversation_history):
    # User message
    with st.container():
        st.markdown(f"""
        <div class="chat-message user-message">
            <b>👤 You:</b><br>
            {turn['user']}
        </div>
        """, unsafe_allow_html=True)
    
    # Show products FIRST (top 3 with confidence indicators)
    if turn.get('products') and len(turn['products']) > 0:
        st.markdown(f"### 🛍️ Top Recommendations (Query {i+1})")
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Products Found", len(turn['products']))
        with col2:
            total_reviews = sum(len(p.get('relevant_reviews', [])) for p in turn['products'])
            st.metric("Review Evidence", total_reviews)
        with col3:
            products_with_reviews = sum(1 for p in turn['products'] if p.get('relevant_reviews'))
            st.metric("Products w/ Evidence", products_with_reviews)
        
        st.markdown("---")
        
        # Show top 3 products
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
                
                # Product info with confidence
                confidence = product_dict.get('confidence_score', product_dict.get('similarity', 0))
                confidence_class = "high-confidence" if confidence > 0.85 else "medium-confidence"
                confidence_emoji = "🟢" if confidence > 0.85 else "🟡"
                
                st.markdown(f"**{product_dict['title'][:60]}...**")
                st.markdown(f"{confidence_emoji} Confidence: {confidence:.1%}")
                
                price = f"${product_dict['price']:.2f}" if product_dict.get('price') else "N/A"
                rating = f"{product_dict['rating']:.1f}★" if product_dict.get('rating') else "N/A"
                
                st.markdown(f"💰 **{price}**")
                st.markdown(f"⭐ **{rating}** ({product_dict.get('num_reviews', 0):,} reviews)")
                
                # Show review evidence count
                relevant_reviews = product_dict.get('relevant_reviews', [])
                if relevant_reviews:
                    st.markdown(f"📝 **{len(relevant_reviews)} relevant reviews**")
                
                st.markdown(f"🔖 `{product_dict['asin']}`")
        
        st.markdown("---")
    
    # THEN show bot explanation text
    with st.container():
        st.markdown(f"""
        <div class="chat-message bot-message">
            <b>🤖 Assistant's Analysis:</b><br>
            {turn['bot']}
        </div>
        """, unsafe_allow_html=True)
    
    # Show detailed products with review evidence
    if turn.get('products') and show_review_evidence:
        with st.expander(f"📦 View All {len(turn['products'])} Products with Review Evidence"):
            for idx, product_dict in enumerate(turn['products'][:max_results], 1):
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Product image
                        if product_dict.get('image_url'):
                            try:
                                st.image(product_dict['image_url'], width=150)
                            except:
                                st.info("📷 No image")
                        else:
                            st.info("📷 No image")
                    
                    with col2:
                        # Product details
                        st.markdown(f"### {idx}. {product_dict['title'][:80]}")
                        
                        price_str = f"${product_dict['price']:.2f}" if product_dict.get('price') else "N/A"
                        rating_str = f"{product_dict['rating']:.1f}★" if product_dict.get('rating') else "N/A"
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.markdown(f"💰 **{price_str}**")
                        with col_b:
                            st.markdown(f"⭐ **{rating_str}**")
                        with col_c:
                            confidence = product_dict.get('confidence_score', product_dict.get('similarity', 0))
                            st.markdown(f"🎯 **{confidence:.1%}**")
                        
                        st.markdown(f"🔖 ASIN: `{product_dict['asin']}`")
                        
                        # Show review evidence
                        relevant_reviews = product_dict.get('relevant_reviews', [])
                        if relevant_reviews:
                            st.markdown(f"**📝 Review Evidence ({len(relevant_reviews)} reviews):**")
                            
                            # Show top 2 reviews
                            for j, review in enumerate(relevant_reviews[:2], 1):
                                st.markdown(f"""
                                <div class="review-evidence">
                                    <b>Review {j}</b> ({review['rating']}★, similarity: {review['similarity']:.2%})<br>
                                    <i>"{review['title']}"</i><br>
                                    {review['text'][:150]}...
                                    {'<br>✅ <i>Verified Purchase</i>' if review.get('verified_purchase') else ''}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No highly relevant reviews found")
                    
                    st.markdown("---")
    
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
            placeholder="e.g., quiet laptop for library work",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 🚀")

# Process user input
if submit_button and user_input:
    with st.spinner("🔍 Searching products and reviews..."):
        try:
            # Step 1: Generate query embedding
            query_embedding = st.session_state.embedding_model.encode_query(user_input)
            
            # Step 2: Unified search (products + reviews)
            products = st.session_state.retriever.search_unified(
                query_embedding=query_embedding,
                strategy=st.session_state.search_strategy,
                top_products=20,
                top_reviews=50
            )
            
            # Step 4: Generate response with review evidence
            # Build rich context
            context_parts = [f"User query: {user_input}\n"]
            context_parts.append(f"\nFound {len(products)} products:\n\n")
            
            for i, product in enumerate(products[:max_results], 1):
                context_parts.append(f"{i}. {product.title}\n")
                context_parts.append(f"   ASIN: {product.asin}\n")
                if product.price:
                    context_parts.append(f"   Price: ${product.price:.2f}\n")
                context_parts.append(f"   Rating: {product.rating:.1f}★ ({product.num_reviews:,} reviews)\n")
                context_parts.append(f"   Confidence: {product.confidence_score:.3f}\n")
                
                if product.relevant_reviews:
                    context_parts.append(f"   📝 {len(product.relevant_reviews)} relevant reviews:\n")
                    for j, review in enumerate(product.relevant_reviews[:2], 1):
                        context_parts.append(f"      {j}. '{review['title']}' ({review['rating']}★)\n")
                        context_parts.append(f"         {review['text'][:150]}...\n")
                context_parts.append("\n")
            
            context = ''.join(context_parts)
            
            response = st.session_state.response_generator.generate_response(
                user_query=user_input,
                products=products,
                conversation_history=st.session_state.conversation_history,
                additional_context=context
            )
            
            # Save to conversation history
            st.session_state.conversation_history.append({
                'user': user_input,
                'bot': response,
                'products': [p.to_dict() for p in products[:max_results]]
            })
            
            # Rerun to show new message
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())

