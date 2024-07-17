from openai import OpenAI
from dotenv import load_dotenv
import csv
import requests
import os

# Load environment variables
load_dotenv()
OPEN_AI_API_KEY_TESTING = os.getenv("OPEN_AI_API_KEY_TESTING")

# Initialize OpenAI client
client = OpenAI(api_key=OPEN_AI_API_KEY_TESTING)

# Constants
CSV_HEADERS = ['id', 'user', 'agent']
LOCAL_ASSISTANT_URL = "http://localhost:5000/api/assistant"
RESET_THREADS_URL = "http://localhost:5000/api/reset_threads"
#CSV_PATH = os.path.join(os.getcwd(), 'data', 'predefined_dialogues_short.csv') # it takes about 5 min to run
CSV_PATH = os.path.join(os.getcwd(), 'data', 'predefined_dialogues.csv') # it takes about 15 min to run
REPORT_PATH = os.path.join('data', 'evaluation_report.csv') 

# Read predefined dialogues from a CSV file
def read_predefined_dialogues(csv_path):
    dialogues = []
    with open(csv_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        
        if headers != CSV_HEADERS:
            print(f"CSV headers do not match expected headers (id, user, agent). Found headers: {headers}")
            return dialogues

        for row in reader:
            if len(row) == 3:
                dialogue = dict(zip(headers, row))
                dialogues.append(dialogue)
    return dialogues

# Query the local assistant with a given dialogue
def query_local_assistant(dialogue):
    payload = {
        "message": dialogue['user'],
        "id": dialogue['id']
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(LOCAL_ASSISTANT_URL, json=payload, headers=headers)
    return response.json().get('response', '').strip()

# Query the external assistant with a prompt
def query_external_assistant(question, predefined_ans, actual_ans):
    prompt = f"""Question: {question}
    Predefined Answer: {predefined_ans}
    Actual Answer: {actual_ans}

    Is the actual answer correct based on the predefined answer? Provide a relevance score between 0.0 to 1.0 based on the question, and also rate the user satisfaction between 0.0 to 1.0 based on the accuracy, relevance and your personal grade to the actual Answer."""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that evaluates LLM answer performance and provides answers in the this format only: true \\n 0.4 \\n 1.0"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Compare predefined and actual responses
def compare_responses(question, predefined_ans, actual_ans):

    response_text = query_external_assistant(question, predefined_ans, actual_ans)
    print(response_text)
    
    lines = response_text.split('\n')
    
    try:
        correctness = True if 'true' in lines[0].strip().lower() else False
        relevance_score = float(lines[1].strip())
        user_satisfaction = float(lines[2].strip())
    except (IndexError, ValueError):
        correctness = False
        relevance_score = 0.0
        user_satisfaction = 0.0

    return correctness, relevance_score, user_satisfaction

# Calculate metrics based on dialogues and responses
def calculate_metrics(dialogues, responses):
    correct_count = 0
    relevance_sum = 0
    satisfaction_sum = 0
    results = []

    for dialogue, response in zip(dialogues, responses):
        correct, relevance, user_satisfaction = compare_responses(dialogue['user'], dialogue['agent'], response)
        results.append((dialogue, response, correct, relevance, user_satisfaction))
        
        if correct:
            correct_count += 1
        relevance_sum += relevance
        satisfaction_sum += user_satisfaction
    
    accuracy = correct_count / len(dialogues)
    avg_relevance = relevance_sum / len(dialogues)
    avg_satisfaction = satisfaction_sum / len(dialogues)

    return results, accuracy, avg_relevance, avg_satisfaction

# Save evaluation report to a CSV file
def save_report(results, accuracy, avg_relevance, avg_satisfaction, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Dialogue ID', 'User', 'Expected Agent', 'Actual Agent', 'Correct', 'Relevance', 'User Satisfaction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for dialogue, response, correct, relevance, user_satisfaction in results:
            writer.writerow({
                'Dialogue ID': dialogue['id'],
                'User': dialogue['user'],
                'Expected Agent': dialogue['agent'],
                'Actual Agent': response,
                'Correct': correct,
                'Relevance': relevance,
                'User Satisfaction': user_satisfaction
            })

        writer.writerow({})
        writer.writerow({'Dialogue ID': 'Metrics'})
        writer.writerow({'User': 'Accuracy', 'Expected Agent': f"{accuracy * 100:.2f}%"})
        writer.writerow({'User': 'Average Relevance', 'Expected Agent': f"{avg_relevance * 100:.2f}%"})
        writer.writerow({'User': 'Average User Satisfaction', 'Expected Agent': f"{avg_satisfaction * 100:.2f}%"})

# Reset the local assistant threads
def reset_threads():
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(RESET_THREADS_URL, headers=headers)
    return response.status_code

# Example usage
predefined_dialogues = read_predefined_dialogues(CSV_PATH)

if not predefined_dialogues:
    print("No dialogues found or incorrect CSV headers. Exiting...")
else:
    reset_status = reset_threads()
    print(f"Reset threads status: {reset_status}")
    responses = [query_local_assistant(dialogue) for dialogue in predefined_dialogues]
    results, accuracy, avg_relevance, avg_satisfaction = calculate_metrics(predefined_dialogues, responses)
    save_report(results, accuracy, avg_relevance, avg_satisfaction, REPORT_PATH)
    reset_threads()

