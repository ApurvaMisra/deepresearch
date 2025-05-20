# BAML Project Readme

This project uses [BoundaryML (BAML)](https://docs.boundaryml.com/) to interact with Large Language Models (LLMs).

## Prerequisites

- Python 3.8+
- `pip` (or your preferred Python package manager like `poetry` or `uv`)
- An OpenAI API key (or other LLM provider keys as configured in `baml_src/main.baml`)

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Set Up Environment Variables:**
    Create a `.env` file in the root of the project and add your API keys:

    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    # Add other API keys if needed
    ```

    The BAML clients will automatically pick up these environment variables.

3.  **Install BAML VSCode/Cursor Extension (Recommended):**
    For the best development experience with BAML, including syntax highlighting, a testing playground, and prompt previews, install the official extension:

    - [BAML VSCode Extension](https://marketplace.visualstudio.com/items?itemName=boundary.baml-extension)

    It's also highly recommended to add the following to your VSCode User Settings for better Python autocompletion:

    ```json
    {
      "python.analysis.typeCheckingMode": "basic"
    }
    ```

4.  **Install Dependencies:**
    Install the BAML Python library and any other project dependencies. If you have a `requirements.txt` file, you can use:

    ```bash
    pip install -r requirements.txt
    ```

    If you don't have one yet, you'll at least need `baml-py` and `python-dotenv` (for loading the `.env` file):

    ```bash
    pip install baml-py python-dotenv
    ```

5.  **Generate the `baml_client`:**
    The `baml_client` directory contains auto-generated Python code to call your BAML functions. Any types defined in `.baml` files are converted into Pydantic models in this directory.
    To generate or update it, run:

    ```bash
    baml-cli generate
    ```

    If you have the VSCode extension installed, it will automatically run `baml-cli generate` whenever you save a `.baml` file.

    _Note: The `baml_src` directory in this project already contains the BAML definitions. The `baml-cli init` command, which creates this directory and starter files, is typically run once when starting a new BAML project._

## Running the Project

(Please add instructions here on how to run your main application, e.g., `python main.py` or `uvicorn app.main:app --reload`)

Example of using a BAML function in Python:

```python
# main.py (example)
import os
from dotenv import load_dotenv
from baml_client import baml as b
from baml_client.types import Message # Assuming Message is defined in your BAML files

load_dotenv() # Load environment variables from .env

def run_chat_example():
    # Make sure OPENAI_API_KEY is set in your environment or .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    initial_state = [
        Message(
            role="user",
            content="I am based in Vancouver, Canada but would be moving to US soon, I want to sign up for Pilates School and learn to become a Pilates instructor. I do want to just focus on Mat Pilates, I have couple of suggestions for the schools but please do your own research based on reviews, popularity which school would be the best and has credibility both in US and Canada. Suggestions: Allmethod, Core community"
        )
    ]
    try:
        response = b.Chat(state=initial_state)
        if hasattr(response, 'action'):
            print(f"Action: {response.action}")
            if response.action == "search_web":
                print(f"Search Query: {response.query}")
            elif response.action == "think":
                print(f"Think Query: {response.query}")
                print(f"Think Context: {response.context}")
            elif response.action == "reply_to_user":
                print(f"Reply Message: {response.message}")
        else:
            # If Chat returns a Message directly (e.g. from an old version or different logic)
            print(f"Response Role: {response.role}")
            print(f"Response Content: {response.content}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_chat_example()
```

## Developing with BAML

- **Modifying BAML files:** Edit files in the `baml_src` directory.
- **Re-generating client:** After making changes to `.baml` files, ensure the `baml_client` is updated by running `baml-cli generate` or by saving the file if you have the VSCode extension.
- **Testing functions:** Use the BAML Playground (available via the VSCode extension) to test your functions. You can also write tests directly in your `.baml` files, like the examples provided in `baml_src/main.baml`.

For more detailed information, refer to the [Official BAML Python Documentation](https://docs.boundaryml.com/guide/installation-language/python).
