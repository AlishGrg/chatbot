import pytest
from app import app
from calculations import calculate_metrics, calculate_single_metric

# test data
projects = [
    {
        "name": "A",
        "initial_cost": 100000,
        "discount_rate": 0.1,
        "cash_flows": [30000, 3000, 10000, 30000, 30000]
    }
]

def test_calculate_single_npv():
    result = calculate_single_metric(projects[0], "npv")
    assert result == "£-23616.74"  # Adjust expected if slightly different

def test_calculate_single_irr():
    result = calculate_single_metric(projects[0], "irr")
    assert "%" in result

def test_calculate_metrics():
    table, rec = calculate_metrics(projects)
    assert "A" in table
    assert "Recommended Project" in rec


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add_project_and_npv(client):
    # clear session
    client.get('/')

    # Add project
    response = client.post('/chat', json={"message": "add project name=A, initial investment=10000, discount rate=0.1, cash flow=[3000 3000 3000 3000 3000]"})
    assert b"added successfully" in response.data

    # calculate NPV
    response = client.post('/chat', json={"message": "calculate npv"})
    assert b"NPV" in response.data or b"npv" in response.data

def test_compare_projects(client):
    client.get('/')

    # Add projects
    client.post('/chat', json={"message": "add project name=A, initial investment=10000, discount rate=0.1, cash flow=[3000 3000 3000 3000 3000]"})
    client.post('/chat', json={"message": "add project name=B, initial investment=5000, discount rate=0.1, cash flow=[2000 2000 2000]"})
    client.post('/chat', json={"message": "add project name=B, initial investment=5000, discount rate=0.08, cash flow=[1000 3000 2000]"})

    # Trigger compare
    response = client.post('/chat', json={"message": "compare projects"})
    assert b"Project Comparison" in response.data
