// main.baml

class Reply {
  action "reply_to_user" @description("reply to the user once we have the compelte result")
  message string
}

class Search {
  action "search_web" @description("search the web for the best options")
  query string
}

class Think {
  action "think" @description("Signal the need to consult the supervisor with the given query and context before proceeding. Context is the conversation history till now")
  query string // The user's original query or the specific topic for supervisor review
  context Message[] // The conversation history and relevant data for the supervisor
}

function Chat(state: Message[]) -> Search | Think | Reply {
  client "openai/gpt-4o-mini-2024-07-18"
  prompt #"
    You are an assistant helping a user with their query. Your goal is to provide the best possible answer by using the tools available to you.

    Your tools are:
    - `search_web`: To search the web for information.
    - `think`: To consult your supervisor for guidance when you are unsure how to proceed.
    - `reply_to_user`: To give the final answer to the user.

    **Conversation Flow:**
    1.  Start by using the `search_web` tool to gather initial information.
    2.  After the search, use the `think` tool to present the findings to your supervisor.
    3.  Your supervisor will provide feedback and instructions. **You MUST follow the supervisor's instructions.**
    4.  If the supervisor tells you to do more research, use the `search_web` tool again with a refined query based on their feedback.
    5.  If the supervisor says the research is complete, use the `reply_to_user` tool to provide the final answer.

    **Output Format:**
    Your output MUST be a single, flat JSON object, without any nesting. Do NOT add any explanations outside of the JSON.
    
    Here is the conversation history:
    {% for m in state %}
    {{ _.role(m.role) }}
    {{ m.content }}
    {% endfor %}

    {{ ctx.output_format }}
  "#
}

function Thinking(query: string, context: Message[]) -> Message {
  client "openai/gpt-4.1"
  prompt #"
    You are a supervisor to an assistant that is helping a user with their query: {{query}}
    You have the following context (the conversation between the assistant, user, and potentially you):
    {{context}}
    
    Your role is to guide the assistant.
    - If the assistant has gathered enough information, help it synthesize the findings and instruct it to reply to the user.
    - If the research is incomplete, provide a summarized analysis of the gathered information and instruct the assistant on what specific details to search for next.
    - If the assistant seems stuck, proactively help it by summarizing the current state and suggesting a clear, actionable next step.

    Format your response as a 'Message' object with your role as 'supervisor'.

    {{ ctx.output_format }}

    ALWAYS listen to the Timetracker role. If it says it is time to reply to the user, ask the assistant to reply to the user.
  "#
}


class Message {
  role "user" | "assistant" | "supervisor" | "Timetracker"
  content string
}


test test_chat_initiates_search {
  functions [Chat]
  args {
    state [
      {
        role "user"
        content "I am based in Vancouver, Canada but would be moving to US soon, I want to sign up for Pilates School and learn to become a Pilates instructor. I do want to just focus on Mat Pilates, I have couple of suggestions for the schools but please do your own research based on reviews, popularity which school would be the best and has credibility both in US and Canada. Suggestions: Allmethod, Core community"
      }
    ]
  }
  @@assert(action_is_search, {{ this.action == "search_web" }})
  @@assert(query_is_correct, {{ this.query == "best Mat Pilates instructor schools US Canada reviews popularity credibility suggestions Allmethod Core community" }})
}

test test_chat_triggers_think_after_search {
  functions [Chat]
  args {
    state [
      {
        role "user",
        content "I want to find the best Pilates schools."
      },
      {
        role "assistant",
        content "The search result for 'best Pilates schools' is: Found School A (good reviews), School B (popular but expensive), School C (new, focuses on Mat Pilates)."
      }
    ]
  }
  @@assert(action_is_think, {{ this.action == "think" }})
  @@assert(think_query_is_correct, {{ this.query == "I want to find the best Pilates schools." }})
  @@assert(think_context_is_correct, {{ this.context == "user: I want to find the best Pilates schools.\nassistant: The search result for 'best Pilates schools' is: Found School A (good reviews), School B (popular but expensive), School C (new, focuses on Mat Pilates)." }})
}

test test_thinking_function {
  functions [Thinking]
  args {
    query "User query: Best Pilates schools. Search results: School A (good), School B (expensive), School C (Mat Pilates focus)."
    context "User: I want to find the best Pilates schools.\nAssistant: Search results: School A (good reviews), School B (popular but expensive), School C (new, focuses on Mat Pilates)."
  }
  @@assert(role_is_supervisor, {{ this.role == "supervisor" }})
  // Check if the content provides some guidance, e.g. mentions a school or next step.
  // This assertion is kept general to avoid LLM brittleness.
  @@assert(content_provides_guidance, {{ ("School C" in this.content or "next step" in this.content or "research further" in this.content or "advise to reply" in this.content) and this.content|length > 10 }})
}

test test_chat_generates_reply_now_thinks_for_supervisor_approval {
  functions [Chat]
  args {
    state [
      {
        role "user",
        content "What is the capital of France?"
      },
      {
        role "assistant",
        content "The search result for 'capital of France' is Paris. This information is confirmed by multiple sources."
      }
    ]
  }
  // Given the Chat prompt "reply action if your supervisor thinks your research is complete",
  // and no supervisor message, the assistant should now use the Think action to consult.
  @@assert(action_is_think, {{ this.action == "think" }})
  @@assert(think_query_is_user_intent, {{ this.query == "What is the capital of France?" }})
  @@assert(think_context_is_current_state, {{ "Paris" in this.context and "user" in this.context }})
}


