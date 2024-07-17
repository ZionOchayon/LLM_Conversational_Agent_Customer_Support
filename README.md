**General Implementation Overview**

I developed the frontend application using React.js and the backend server using
Python (Flask). The frontend and backend communicate using RESTful API
architecture.

To implement the conversational agent, I used the OpenAI Assistant API along with a
vector store and thread management system to handle multiple conversations
simultaneously. Each thread ID is linked to a chat ID stored in a NoSQL database.
For the assistant's functionalities, I utilized file search with stored FAQs and the function
API with tool calls to handle multiple functions concurrently. Additionally, a NoSQL
database is used to store order statuses.

For evaluation, I created a script that runs all predefined dialogues and evaluates each
result with diffrent conversational agent. This ensures the accuracy and efficiency of the
agent's responses.

**Detailed File Descriptions**

**Flask Server**
  **1. app.py:**
    • The primary file for the Flask application.
    • Manages incoming requests, interacts with the assistant, and handles
      threads.
     
  **2. createAssistant.py:**
    • Contains the code for creating the assistant.
      
  **3. createOrdersDatabase.py:**
    • Contains the code for creating the orders database.
      
  **4. testing.py:**
    • Contains the code for running all predefined dialogues and generating
      evaluation reports.
  
  **5. .env:**
      • Contains environment variables, such as API keys.
     
  **6. contact_info.csv:**
    • Contains saved contact data.

  **7. databases\threads_db:**
    • Database for handling multi-conversations, each as a separate thread.
    • The threads_db will reset upon new entry or frontend page refresh due to
      the lack of user registration.
      
  **8. databases\orders_db:**
    • Database for storing all order statuses.

  **9. Data folder:**
    • Contains all data used by the assistant and testing script, such as insaitfaq and predefined dialogues.
    • Also contains the generated evaluation report.

**Client**
  **1. Src\app.js:**
    o Main React application component.
  **2. Src\app.css:**
    o Styles for the React application.

**Setting Up the Environment**

**Prerequisites**
Ensure you have the following installed on your machine:
  1. Node.js (with npm)
  2. Python (preferably 3.7 or later)

**Step 1: Extract Files from ZIP Archive**
  1. Download the ZIP archive containing your project and extract it to your local
     machine.
  2. Locate the ZIP file (LLM_Conversational_Agent_Customer_Support.zip).
  3. Extract the contents of the ZIP file to a directory.
     
**Step 2: Set Up the Flask Server**
  1. Navigate to the flask-server directory:
      cd LLM_Conversational_Agent_Customer_Support/flask-server
     
  2. Activate the existing virtual environment:
    o On Windows:
      .\venv\Scripts\activate
    o On macOS/Linux:
      source venv/bin/activate
     
  3. Install the required Python packages:
      pip install -r requirements.txt
     
  4. Run the Flask server:
      flask run
     
  The Flask server should now be running on http://127.0.0.1:5000.

  **Step 3: Set Up the React App**
  1. Open a new terminal.

  2. Navigate to the client directory:
      cd client

  3. Run the React app:
      npm start

  The React app should now be running on http://127.0.0.1:3000.

**Running the Application**
1. Start the Flask server:
  cd flask-server
  source venv/bin/activate or .\venv\Scripts\activate
  flask run

3. Open a new terminal.

4. Start the React app:
   cd client
   npm start

5. Open the link http://127.0.0.1:3000.

**Running the Testing**
**Note:** Ensure the React app is closed (press Ctrl+C in the React app terminal) before
running the testing. Running both simultaneously can lead to issues with thread
management.

**Note:** In testing.py at lines 18-19, you can choose between a long test (15 min) and a
short test (5 min), depending on the number of predefined dialogues.

1. Start the Flask server:
  cd flask-server
  source venv/bin/activate or .\venv\Scripts\activate
  flask run

2. Open a new terminal.

3. Run the testing script:
  cd flask-server
  source venv/bin/activate or .\venv\Scripts\activate
  python testing.py

**After testing is complete, an evaluation report will be generated in the data folder.**
