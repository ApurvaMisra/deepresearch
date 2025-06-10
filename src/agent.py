import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baml_client import b
from baml_client.types import Search, Think, Reply, Message
import requests
from dotenv import load_dotenv
import json

# Load env variables from .env file
# Construct the path to the .env file, assuming it's in the parent directory of this script's directory
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

st.set_page_config(page_title="Deep Research Agent", page_icon="🤖")
st.title("🤖 Deep Research Agent")
st.caption("This agent performs deep research on a given topic, consulting a supervisor for guidance.")


# Initialize state
if "state" not in st.session_state:
    st.session_state.state = []
if "processing" not in st.session_state:
    st.session_state.processing = False


def get_search_results(query: str) -> str:
    """Use serp api to get the search results and return a summarized version."""
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        st.error("SERP_API_KEY not found. Search will return an error message.")
        return "Error: SERP_API_KEY not configured."
    serp_api_url = f"https://serpapi.com/search.json?api_key={api_key}&q={query}"
    try:
        response = requests.get(serp_api_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        
        # Extract and summarize the organic results
        if "organic_results" in data:
            summary = []
            for result in data["organic_results"][:5]: # Limit to top 5 results
                title = result.get("title", "No Title")
                link = result.get("link", "#")
                snippet = result.get("snippet", "No snippet available.")
                summary.append(f"Title: {title}\\nLink: {link}\\nSnippet: {snippet}\\n---")
            return "\\n".join(summary)
        else:
            return "No organic results found."

    except requests.exceptions.RequestException as e:
        st.error(f"Error during SerpAPI request: {e}")
        return f"Error fetching search results: {e}"
    except json.JSONDecodeError:
        st.error("Failed to parse search results.")
        return "Error: Failed to parse search results."


def run_agent_step():
    if not st.session_state.processing:
        return

    max_steps = 4
    # Check if max steps reached and Timetracker message hasn't been added yet.
    if len(st.session_state.state) > (max_steps * 2):
        is_timetracker_sent = any(m.role == "Timetracker" for m in st.session_state.state)
        if not is_timetracker_sent:
            st.warning(f"Reached maximum steps ({max_steps}). Forcing a reply.")
            st.session_state.state.append(Message(role="Timetracker", content="MAXIMUM PROCESSING STEPS REACHED. TIME TO REPLY TO THE USER"))
            # Do not stop processing, let the agent call the supervisor one last time.
    
    # Add a fallback for very long conversations to prevent infinite loops.
    if len(st.session_state.state) > (max_steps * 2) + 4:
        st.error("Agent is stuck in a loop. Halting.")
        st.session_state.state.append(Message(role="assistant", content="I seem to be stuck in a loop. Please try rephrasing your query."))
        st.session_state.processing = False
        return


    action = b.Chat(st.session_state.state)

    if isinstance(action, Search):
        with st.chat_message("assistant"):
            with st.spinner(f"Searching for: {action.query}"):
                search_result = get_search_results(action.query)
                content = f"The search result for {action.query} is {search_result}"
                st.session_state.state.append(Message(role="assistant", content=content))

    elif isinstance(action, Think):
         with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                supervisor_message_obj: Message = b.Thinking(query=action.query, context=st.session_state.state)
                st.session_state.state.append(supervisor_message_obj)

    elif isinstance(action, Reply):
        st.session_state.state.append(Message(role="assistant", content=action.message))
        st.session_state.processing = False
    
    else:
        # Handle cases where the action is not recognized
        st.error(f"Unknown action: {action}")
        st.session_state.processing = False


# Display chat messages from history
i = 0
while i < len(st.session_state.state):
    message = st.session_state.state[i]

    is_final_reply = (message.role == 'assistant' and 
                      not st.session_state.processing and 
                      i == len(st.session_state.state) - 1)

    if message.role == 'user':
        with st.chat_message("user"):
            st.markdown(message.content)
        i += 1
    elif is_final_reply:
        with st.chat_message("assistant"):
            st.markdown(message.content)
        i += 1
    else:
        # It's an internal conversation turn (assistant, supervisor, timetracker)
        with st.expander("🤔 Agent's Internal Work...", expanded=True):
            while i < len(st.session_state.state):
                
                current_message_is_final = (st.session_state.state[i].role == 'assistant' and 
                                            not st.session_state.processing and 
                                            i == len(st.session_state.state) - 1)
                
                if st.session_state.state[i].role == 'user' or current_message_is_final:
                    break

                inner_message = st.session_state.state[i]
                
                avatar = "🤖" # default for assistant
                if inner_message.role == 'supervisor':
                    avatar = "🧑‍🏫"
                elif inner_message.role == 'Timetracker':
                    avatar = "⏱️"
                
                with st.chat_message(inner_message.role, avatar=avatar):
                    st.markdown(inner_message.content)
                i += 1

# Accept user input
if prompt := st.chat_input("What is your research query?"):
    # Add user message to chat history
    st.session_state.state.append(Message(role="user", content=prompt))
    st.session_state.processing = True
    st.rerun()


if st.session_state.processing:
    run_agent_step()
    st.rerun()


