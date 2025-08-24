from flask import Flask, render_template, request, jsonify, session
from calculations import calculate_metrics,calculate_single_metric
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import yaml
from difflib import get_close_matches
import os



# ========== GLOBAL ==========
qa_data = []  # Loaded from YAML

# ========== YAML LOADING & TRAINING ==========

def load_qa_pairs_from_yaml(file_path):
    global qa_data
    if not os.path.exists(file_path):
        print("⚠️ YAML file not found!")
        return []

    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        qa_data = data.get('project_management', [])
        return [(item['question'], item['answer']) for item in qa_data]

def train_bot_from_yaml(bot, yaml_path):
    trainer = ListTrainer(bot)
    qa_pairs = load_qa_pairs_from_yaml(yaml_path)
    for question, answer in qa_pairs:
        trainer.train([question, answer])

def get_fuzzy_answer(user_input):
    questions = [item['question'] for item in qa_data]
    match = get_close_matches(user_input, questions, n=1, cutoff=0.6)
    if match:
        for item in qa_data:
            if item['question'] == match[0]:
                return item['answer']
    return None

# ===== Initialize and train chatbot =====
chatbot = ChatBot(
    "ProjectBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///db.sqlite3",
    read_only=True
)
train_bot_from_yaml(chatbot, "pm_knowledge.yaml")  # YAML file path

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Necessary for session management

@app.route("/")
def index():
    # Clear all session-stored project data on refresh
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    if 'projects' not in session:
        session['projects'] = []
    projects = session['projects']
    user_input = request.json['message'].strip().lower()
    # Access the current project from the session
    current_project = session.get('current_project', {})

    user_input = request.json['message'].strip().lower()

    if user_input.lower().startswith("compare projects"):
        if not projects:
            return jsonify({"reply": "❌ No projects entered yet. Please add some first."})
        
        table, summary = calculate_metrics(projects)
        full_reply = f"📊 <b>Project Comparison:</b><br><pre>{table}</pre><br>{summary}"
        return jsonify({"reply": full_reply})

    if user_input.startswith("add project"):
        try:
            parts = user_input[len("add project "):]
            name_part, cost_part, rate_part, cf_part = parts.split(",")
            name = name_part.split("=")[1].strip()
            cost = float(cost_part.split("=")[1])
            rate = float(rate_part.split("=")[1])
            cf_raw = cf_part.split("=")[1].strip("[] ")
            cash_flows = list(map(float, cf_raw.replace(",", " ").split()))

            project = {
                "name": name,
                "initial_cost": cost,
                "discount_rate": rate,
                "cash_flows": cash_flows
            }

            # Check for duplicate project names
            if any(p['name'].lower() == name.lower() for p in projects):
                return jsonify({"reply": f"⚠️ A project with the name '<b>{name.upper()}</b>' already exists. Please choose a different name."})

            # Add new project
            projects.append(project)
            session['projects'] = projects  # Save updated list back to session
            session['current_project'] = project
            return jsonify({"reply": f"✅ Project '<b>{name.upper()}</b>' added successfully."})
        except Exception as e:
            return jsonify({"reply": f"❌ Failed to add project. Please check your input format. For Example: 'add project name=A, initial investment=10000, discount rate=10, cash flow=[2000 3000 4000 ..]'."})

    elif user_input.startswith("calculate"):
        if not current_project:
            return jsonify({"reply": "❌ No project found. Please first add a project using the format:\n <b>add project name=A, initial investment=10000, discount rate=0.10, cash flow=[2000 3000 4000 ..]</b>"})
        try:
            metric = user_input.replace("calculate", "").strip()
            result = calculate_single_metric(current_project, metric)
            return jsonify({"reply": f"📊 <b>{metric.upper()}</b> for given Project is: {result}"})
        except Exception as e:
            return jsonify({"reply": f"❌ Error calculating {metric}. {str(e)}"})
        
    fuzzy_answer = get_fuzzy_answer(user_input)
    if fuzzy_answer:
        return jsonify({"reply": fuzzy_answer})
    response = chatbot.get_response(user_input)
    return jsonify({"reply": str(response)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)