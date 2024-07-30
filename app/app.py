import streamlit as st
import uuid

def print_log(*message):
    print(*message, flush=True)

def main():
    print_log("Starting the Course Assistant application")
    st.title("Course Assistant")

    # Session state initialization
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
    if 'count' not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")
    if 'submitted' not in st.session_state:
        print('SUBMISSION !!!!!!!!!!!!!!!!!!!!')
        st.session_state.submitted = False

    # Course selection
    course = st.selectbox(
        "Select a course:",
        ["machine-learning-zoomcamp", "data-engineering-zoomcamp", "mlops-zoomcamp"]
    )
    print_log(f"User selected course: {course}")

    # Model selection
    model_choice = st.selectbox(
        "Select a model:",
        ["ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"]
    )
    print_log(f"User selected model: {model_choice}")

    # Search type selection
    search_type = st.radio(
        "Select search type:",
        ["Text", "Vector"]
    )
    print_log(f"User selected search type: {search_type}")

    # User input
    user_input = st.text_input("Enter your question:")

    if st.button("Submit"):
        print_log(f"User submitted question: {user_input}")
        st.write(f"Question submitted: {user_input}")
        st.session_state.submitted = True

    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1", disabled=not st.session_state.submitted):
            st.session_state.submitted = False
            st.session_state.count += 1
            print_log(f"Positive feedback received. New count: {st.session_state.count}")
            st.rerun()
    with col2:
        if st.button("-1", disabled=not st.session_state.submitted):
            st.session_state.submitted = False
            st.session_state.count -= 1
            print_log(f"Negative feedback received. New count: {st.session_state.count}")
            st.rerun()

    st.write(f"Current count: {st.session_state.count}")

if __name__ == "__main__":
    main()
