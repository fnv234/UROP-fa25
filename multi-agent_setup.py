"""
This file will have:
  - ForioClient: connector to Forio simulation (data extraction & results)
  - ExecutiveBot: C-level roles linked to KPIs
  - BoardRoom: multi-agent environment to simulate meetings

See pdf of plan outline for general initial thoughts.
"""

import requests

## connect to simulation
class ForioClient:
    """
    Handles interaction with the Forio cyber-risk simulation API.
    - run_simulation: submit decision parameters and start a run
    - get_results: fetch output KPIs for analysis
    """

    def __init__(self, base_url, user, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (user, password)

    def run_simulation(self, params):
        """Run one simulation with given decision params"""
        response = self.session.post(f"{self.base_url}/runs", json=params)
        response.raise_for_status()
        return response.json()

    def get_results(self, run_id):
        """Extract output variables after simulation finishes"""
        response = self.session.get(f"{self.base_url}/runs/{run_id}/results")
        response.raise_for_status()
        return response.json()


## executive bot for single-agent decision making
class ExecutiveBot:
    """
    Represents a board-level executive agent
    Each bot:
      - Focuses on a KPI (profit, risk, availability, etc.)
      - Has targets (desired ranges for KPI)
      - Has a personality (risk tolerance, friendliness, ambition)
    """

    def __init__(self, name, kpi_focus, target=None, personality=None):
        self.name = name
        self.kpi_focus = kpi_focus
        self.target = target or {}
        self.personality = personality or {
            "risk_tolerance": 0.5,
            "friendliness": 0.5,
            "ambition": 0.5
        }

    def evaluate(self, results):
        """Judge simulation outputs according to role focus and personality."""
        kpi_value = results.get(self.kpi_focus, None)
        if kpi_value is None:
            return f"{self.name}: KPI {self.kpi_focus} not found."

        status = "on target"
        if self.target:
            if kpi_value < self.target.get("min", float("-inf")):
                status = "below target"
            elif kpi_value > self.target.get("max", float("inf")):
                status = "above target"

        return f"{self.name} sees {self.kpi_focus}={kpi_value}, status={status}"

## boardroom for multi-agent interaction
class BoardRoom:
    """
    Represents a meeting of bots
    - run_meeting: collect evaluations from all bots
    - simulate_interaction: simulate collaborative vs hostile dynamics
    """

    def __init__(self, bots):
        self.bots = bots

    def run_meeting(self, results):
        """Let all bots provide feedback on a simulation run."""
        feedback = []
        for bot in self.bots:
            feedback.append(bot.evaluate(results))
        return feedback

    def simulate_interaction(self, setting="collaborative"):
        """Simplified placeholder for bot dynamics."""
        if setting == "collaborative":
            return "Bots align toward compromise."
        elif setting == "hostile":
            return "Bots argue, no consensus."
        else:
            return "Neutral interaction."

## sample workflow, to be edited/continued
if __name__ == "__main__":
    client = ForioClient(
        base_url="http://forio.com/app/mitcams/cyberriskmanagement-ransomeware-2023",
        user="MIT@2025002",
        password="MIT@2025002"
    )

    params = {"prevention_budget": 50, "detection_budget": 30, "response_budget": 20}
    run = client.run_simulation(params)
    results = client.get_results(run["id"])

    cfo = ExecutiveBot("CFO", "accumulated_profit", target={"min": 1000000})
    cro = ExecutiveBot("CRO", "compromised_systems", target={"max": 10})
    coo = ExecutiveBot("COO", "systems_availability", target={"min": 0.95})

    board = BoardRoom([cfo, cro, coo])
    feedback = board.run_meeting(results)

    print("Board Feedback:")
    for f in feedback:
        print(" -", f)

    print("Interaction:", board.simulate_interaction(setting="collaborative"))
