from baml_client import b
from baml_client.types import Search, Think, Reply, Message
import requests
import os
from dotenv import load_dotenv

#load env variables from .env file
# Construct the path to the .env file, assuming it's in the parent directory of this script's directory
dotenv_path = os.path.join('/Users/apurvamisra/Documents/code/deep_research/src/.env')
load_dotenv(dotenv_path=dotenv_path)
# We call a model once
message = """I am based in Vancouver, Canada but would be moving to US soon, I want to sign up for Pilates School and learn to become a Pilates instructor. I do want to just focus on Mat Pilates, I have couple of suggestions for the schools but please do your own research based on reviews, popularity which school would be the best and has credibility both in US and Canada

Suggestions: 
Allmethod
Core community"""

def agent(start: str) -> str:
  state = [Message(role="user", content=start)]
  max_steps = 6
  current_step = 0
  
  while True:
    current_step += 1
    if current_step > max_steps:
      print(f"Reached maximum steps ({max_steps}). Generating a summary reply.")
      state.append(Message(role="Timetracker", content="MAXIMUM PROCESSING STEPS REACHED. TIME TO REPLY TO THE USER"))
      print("*"*35)
      print(state)
    action = b.Chat(state)
    
    if isinstance(action, Search):
        # Technically, get_weather could be using another LLM
        # (sub-agent). But as long as we know what type it
        # returns, we can have very clean constructs.
        search_result = get_search_results(action.query)
        # How you embed the context, matters!
        # instead of adding in JSON, I'm choosing to make 
        # this more readable.
        content = f"The search result for {action.query} is {search_result}"
        state.append(Message(role="assistant", content=content))
    
    if isinstance(action, Think):
        # Call the supervisor. action.query and action.context are inputs for the supervisor.
        supervisor_message_obj: Message = b.Thinking(query=action.query, context=str(state))
        # Add the supervisor's exact message (which has role="supervisor") to the state.
        state.append(supervisor_message_obj)
    
    if isinstance(action, Reply): 
        # I've handled everything for the user.
        return action.message
    
def get_search_results(query: str) -> str:
   #Use serp api to get the search results
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        print("SERP_API_KEY not found. Search will return an error message.")
        return "Error: SERP_API_KEY not configured."
    serp_api_url = f"https://serpapi.com/search.json?api_key={api_key}&q={query}"
    try:
        response = requests.get(serp_api_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during SerpAPI request: {e}")
        return f"Error fetching search results: {e}"

def think(query: str, context: str) -> str:
   # This function is effectively replaced by direct call to b.Thinking in the agent loop
   # and processing its Message object.
   # If you still need this function for other purposes, it should be:
   supervisor_message: Message = b.Thinking(query, context)
   return supervisor_message.content # Or handle the Message object as needed


if __name__ == "__main__":
  print(agent(message))


