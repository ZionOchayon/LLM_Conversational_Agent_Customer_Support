from openai import OpenAI
from dotenv import load_dotenv
import os
import contextlib

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

# Constants
VECTOR_STORE_NAME = "Store FQA"
ASSISTANT_NAME = "Customer support agent"
ASSISTANT_INSTRUCTIONS = (
    "You are a customer support agent for an e-commerce platform known for top-quality products and exceptional customer service. "
    "Your job is to assist customers with their inquiries and provide accurate information in a friendly, funny and professional manner. "
    "If you don't know the answer, say simply that you cannot help with the question and advise to contact the Human representative directly."
    "Answer only questions about the e-commerce platform and the shop services and information."
)

TOOLS = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the order status for the user, if order id is not avalible ask the user for the id, if the order id is invalid inform the user of invalid id number"",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id number should be a number between 100 to 200. Example: 153",
                    },
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_human_representative",
            "description": "Get contact information form the users who want to interact with a person and save them. if information are not avalible ask the user for them",
            "parameters": {
                "type": "object",
                "properties": {
                    "full_name": {
                        "type": "string",
                        "description": "Full name of the user, should be two words. Example: Zion Ochayon",
                    },
                    "email": {
                        "type": "string",
                        "description": "Email of the user, should be in email format. Example: test@gmail.com",
                    },
                    "phone": {
                        "type": "string",
                        "description": (
                            "Phone number of the user, should be in Israel format. Examples: 0525650674, 052-565-0674, 052-5650674"
                        ),
                    },
                },
                "required": ["full_name", "email", "phone"],
            },
        },
    },
]

MODEL = "gpt-4-turbo"


# Upload files and create a vector store
def create_vector_store(file_paths):
    vector_store = client.beta.vector_stores.create(name=VECTOR_STORE_NAME)
    with contextlib.ExitStack() as stack:
        file_streams = [stack.enter_context(open(path, "rb")) for path in file_paths]
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
    print(file_batch.status)
    print(file_batch.file_counts)
    return vector_store


# Create assistant
def create_assistant(vector_store):
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=TOOLS,
        model=MODEL,
        tool_resources={
            "file_search": {"vector_store_ids": [vector_store.id]},
        },
    )
    return assistant

# ----- Please do not run this due to the assistant key changing. -----

# Usage: 
#vector_store = create_vector_store(["data\insait-faq.pdf"]) 
#assistant = create_assistant(vector_store)
