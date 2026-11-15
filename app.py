import streamlit as st
from rag_pipeline import generate_answer
from knowledge_graph import render_knowledge_graph

# Configure the web page settings
st.set_page_config(page_title="CourseCompass AI", page_icon="🎓", layout="centered")

# --- OPTIMIZATION: Caching the API response ---
@st.cache_data(show_spinner=False)
def get_cached_answer(query):
    """Caches the API response to reduce latency on repeated queries."""
    return generate_answer(query)

# Build the UI Header
st.title("🎓 CourseCompass")
st.subheader("RAG-Powered Academic Search Engine & Knowledge Graph")
st.markdown("Ask any question regarding your course syllabus, prerequisites, or learning outcomes.")

# Create the input text box for the user
user_query = st.text_input("Enter your query:", placeholder="e.g., What prerequisites are required to understand deep learning?")

# Handle the search button click
if st.button("Search Syllabus"):
    if user_query.strip():
        # Show a loading spinner while the backend works
        with st.spinner("Retrieving documents and generating AI response (Please wait)..."):
            
            # Use the optimized cached function instead of direct API call
            final_answer = get_cached_answer(user_query)
            
            # Display the final AI text output
            st.markdown("### 🤖 AI Response:")
            st.info(final_answer)
            
            # Display the visual Knowledge Graph
            st.markdown("### 📊 Curriculum Knowledge Graph")
            st.markdown("*Visual representation of course dependencies based on syllabus logic.*")
            
            kg_figure = render_knowledge_graph(user_query)
            st.pyplot(kg_figure)
            
    else:
        st.warning("Please enter a valid question before clicking search.")
        
# Footer for a professional look
st.markdown("---")
st.markdown("Developed for Information Retrieval Course Project")