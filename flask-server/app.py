from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from openai import OpenAI
from dotenv import load_dotenv
import shelve
import os
import time
import csv
import json

# Load environment variables
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Initialize OpenAI client
client = OpenAI(api_key=OPEN_AI_API_KEY)

# Initialize Flask app and enable CORS globally
app = Flask(__name__)
CORS(app)

# Constants
DB_FOLDER = 'databases'
THREADS_DB = os.path.join(DB_FOLDER, "threads_db")
ORDERS_DB = os.path.join(DB_FOLDER, "orders_db")
CONTACT_INFO_FILE = 'contact_info.csv'
FIELDNAMES = ['full_name', 'email', 'phone']

# Thread management
def check_if_thread_exists(wa_id):
    with shelve.open(THREADS_DB) as threads_shelf:
        return threads_shelf.get(wa_id)

def store_thread(wa_id, thread_id):
    with shelve.open(THREADS_DB, writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

def reset_threads_db():
    with shelve.open(THREADS_DB, writeback=True) as threads_shelf:
        threads_shelf.clear()

# Verify the orders database
def verify_database(db_name):
    with shelve.open(ORDERS_DB) as db:
        for order_id in range(100, 201):
            print(f'Order ID: {order_id}, Status: {db[str(order_id)]}')

# Save contact information to CSV
def save_contact_information(contact_info):
    file_exists = os.path.isfile(CONTACT_INFO_FILE)
    with open(CONTACT_INFO_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(contact_info)
    return "We saved your contact details and will contact you soon."

# Get Order status
def check_order_status(order_id):
    with shelve.open(ORDERS_DB) as db:
        return db.get(str(order_id), "Order ID not found")

# Generate response
def generate_response(message_body, wa_id):
    thread_id = check_if_thread_exists(wa_id)

    if thread_id is None:
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
    else:
        thread = client.beta.threads.retrieve(thread_id)

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    return run_assistant(thread)

# Run assistant
def run_assistant(thread):
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status not in ["requires_action", "completed", "failed"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(run.status)

    if run.status == "requires_action":
        submit_tools_outputs(run, thread)
    
    if run.status == "failed":
        return "There was an error completing your request. Please try again."

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value

    print(messages)
    print(new_message)

    return new_message

def submit_tools_outputs(run, thread):
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = list(map(get_outputs_for_tool_call, tool_calls))

    tool_outputs = [output for output in tool_outputs if output['output'] != 'Input Error']

    while run.status != "completed":
        time.sleep(0.5)
        if run.status == "requires_action" and tool_outputs:
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
            )
        else:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(run.status)

def get_outputs_for_tool_call(tool_call):
    arguments = json.loads(tool_call.function.arguments)
    name = tool_call.function.name
    if name is None:
        func_result = 'Input Error'
    elif 'request_human' in name:
        func_result = save_contact_information(arguments)
    elif 'order_status' in name:
        func_result = check_order_status(arguments['order_id'])
    else:
        func_result = 'Input Error'
    return {
        "tool_call_id": tool_call.id,
        "output": func_result
    }

# Flask routes
@app.route('/api/assistant', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'])
def assistant():
    data = request.get_json()
    message_body = data.get('message')
    wa_id = data.get('id')

    if not message_body or not wa_id:
        return jsonify({"error": "Invalid input"}), 400

    response = generate_response(message_body, wa_id)
    return jsonify({"response": response})

@app.route('/api/reset_threads', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'])
def reset_threads():
    reset_threads_db()
    verify_database('orders_db')
    return jsonify({"message": "Threads database reset successfully."})

if __name__ == '__main__':
    app.run(debug=True)
