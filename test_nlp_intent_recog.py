import pytest
from app import get_fuzzy_answer, load_qa_pairs_from_yaml, chatbot

# Load your YAML data once for testing fuzzy matching
@pytest.fixture(scope="module", autouse=True)
def load_data():
    load_qa_pairs_from_yaml("pm_knowledge.yaml")  # adjust path if needed

def test_get_fuzzy_answer_exact_match():
    user_question = "what is project scope"
    answer = get_fuzzy_answer(user_question)
    assert answer is not None and len(answer) > 0

def test_get_fuzzy_answer_close_match():
    user_question = "formula for roi"
    answer = get_fuzzy_answer(user_question)
    assert answer is not None  # fuzzy should catch close match

def test_chatbot_response():
    user_message = "hello"
    response = chatbot.get_response(user_message)
    assert response is not None
    assert len(str(response)) > 0
