# from flask import Flask, render_template, request, jsonify
# from chatterbot import ChatBot
# from chatterbot.trainers import ChatterBotCorpusTrainer
# from calculations import calculate_metrics, calculate_single_metric

# app = Flask(__name__)

# chatbot = ChatBot("ProjectBot")
# trainer = ChatterBotCorpusTrainer(chatbot)
# trainer.train("chatterbot.corpus.english")

# projects = []
# roi = []

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chat", methods=["POST"])
# def chat():
#     global current_project
#     user_input = request.json['message']

    
#     if user_input.lower().startswith("compare projects"):
#         if not projects:
#             return jsonify({"reply": "❌ No projects entered yet. Please add some first."})
        
#         table, summary = calculate_metrics(projects)
#         full_reply = f"📊 <b>Project Comparison:</b><br><pre>{table}</pre><br>{summary}"
#         return jsonify({"reply": full_reply})

#     if user_input.lower().startswith("add project"):
#         try:
#             parts = user_input[len("add project "):]
#             name_part, cost_part, rate_part, cf_part = parts.split(",")
#             name = name_part.strip()
#             cost = float(cost_part.split("=")[1])
#             rate = float(rate_part.split("=")[1])
#             cf_raw = cf_part.split("=")[1].strip("[] ")
#             cash_flows = list(map(float, cf_raw.split()))
#             projects.append({
#                 "name": name,
#                 "initial_cost": cost,
#                 "discount_rate": rate,
#                 "cash_flows": cash_flows
#             })
#             return jsonify({"reply": f"✅ Project '<b>{name}</b>' added successfully."})
#         except Exception as e:
#             return jsonify({"reply": f"❌ Failed to add project. Make sure format is correct. Error: {str(e)}"})
        
#     elif user_input.startswith("calculate"):
#         if not current_project:
#             return jsonify({"reply": "❌ Please add a project first using 'add project' command."})
#         try:
#             metric = user_input.replace("calculate", "").strip()
#             result = calculate_single_metric(current_project, metric)
#             return jsonify({"reply": f"📊 <b>{metric.upper()}:</b> {result}"})
#         except Exception as e:
#             return jsonify({"reply": f"❌ Error calculating {metric}. {str(e)}"})   
#     # if user_input.lower().startswith("calculate"):
#     #     return jsonify({"reply": "🤖 I can help you calculate NPV, IRR, ROI, Payback or BCR after you add a project. Please enter 'calculate ROI' or 'Calculate NPV' and so on to calculate "})
    
#     # if user_input.lower().startswith("calculate ROI"):
#     #     return jsonify({"reply": "🤖 Please add project name, initial investment and annual cashflows like add project_name, initial_investment, Annual cashflow like [3000 3000 3000 ...]"})
    
#     # if user_input.lower().startswith("add"):
#     #     try:
#     #         parts = user_input[len("add "):]
#     #         name_part, cost_part, cf_part = parts.split(",")
#     #         name = name_part.strip()
#     #         cost = float(cost_part.split("=")[1])
#     #         cf_raw = cf_part.split("=")[1].strip("[] ")
#     #         cash_flows = list(map(float, cf_raw.split()))
#     #         roi.append({
#     #             "name": name,
#     #             "initial_cost": cost,
#     #             "cash_flows": cash_flows
#     #         })
#     #         return jsonify({"reply": f"✅ Project '<b>{name}</b>' added successfully."})
#     #     except Exception as e:
#     #         return jsonify({"reply": f"❌ Failed to add project. Make sure format is correct. Error: {str(e)}"})

    

#     response = chatbot.get_response(user_input)
#     return jsonify({"reply": str(response)})



# if __name__ == "__main__":
#     app.run(debug=True)



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
train_bot_from_yaml(chatbot, "pm_knowledge.yaml")  # Your YAML file path

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Necessary for session management

# ========== Setup ChatterBot ==========
# chatbot = ChatBot("ProjectAdvisor", read_only=True)
# trainer = ChatterBotCorpusTrainer(chatbot)
# trainer.train("chatterbot.corpus.english")

# # ========== Load YAML Knowledge Base ==========
# with open("pm_knowledge.yaml", "r") as file:
#     pm_data = yaml.safe_load(file)["project_management"]

# # ========== PM Question Matching ==========
# def match_pm_question(user_input):
#     questions = [item["question"].lower() for item in pm_data]
#     match = get_close_matches(user_input.lower(), questions, n=1, cutoff=0.6)
#     if match:
#         for item in pm_data:
#             if item["question"].lower() == match[0]:
#                 return item["answer"]
#     return "Sorry. I can't find anything meaningful for you at the moment... :)"

@app.route("/")
def index():
    # # Clear project data on page load to reset state
    # session.pop('current_project', None)  # This ensures that the current project is cleared when page is loaded
    # return render_template("index.html")

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

            # if any(p['name'].lower() == name.lower() for p in projects):
            #     return jsonify({"reply": f"⚠️ A project with the name '<b>{name.upper()}</b>' already exists. Please choose a different name."})

            project = {
                "name": name,
                "initial_cost": cost,
                "discount_rate": rate,
                "cash_flows": cash_flows
            }

            # # Prevent duplicates
            # if not any(p['name'].lower() == name.lower() for p in projects):
            #     projects.append(project)
            #     session['projects'] = projects  # Save updated list back to session


            # # Save current project also for single metric calculations
            # session['current_project'] = project
            # return jsonify({"reply": f"✅ Project '<b>{name.upper()}</b>' added successfully."})

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
            return jsonify({"reply": "❌ No project found. Please add a project first using the format: 'add project name=A, initial investment=10000, discount rate=0.10, cash flow=[2000 3000 4000 ..]'."})
        try:
            metric = user_input.replace("calculate", "").strip()
            result = calculate_single_metric(current_project, metric)
            return jsonify({"reply": f"📊 <b>{metric.upper()}</b> for given Project is: {result}"})
        except Exception as e:
            return jsonify({"reply": f"❌ Error calculating {metric}. {str(e)}"})
        
    fuzzy_answer = get_fuzzy_answer(user_input)
    if fuzzy_answer:
        return jsonify({"reply": fuzzy_answer})

    # return jsonify({"reply": " I can help you calculate NPV, IRR, ROI, Payback or BCR after you add a project."})
    response = chatbot.get_response(user_input)
    return jsonify({"reply": str(response)})

if __name__ == "__main__":
    app.run(debug=True)