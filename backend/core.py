# backend/core.py

from backend.agents.prosecution_agent import ProsecutionAgent
from backend.agents.defense_agent import DefenseAgent
from backend.agents.cross_examiner_agent import CrossExaminerAgent
from backend.agents.judge_agent import JudgeAgent

class CourtroomSimulator:
    def __init__(self):
        """
        Initialize all courtroom agents.
        """
        self.prosecutor = ProsecutionAgent()
        self.defense = DefenseAgent()
        self.cross_examiner = CrossExaminerAgent()
        self.judge = JudgeAgent()

    def run_trial(self, crime_description):
        """
        Run the full mock courtroom simulation based on the given crime description.
        Returns a structured trial result.
        """
        print("🏛️ Starting mock courtroom simulation...\n")

        # Step 1: Prosecution builds its case
        prosecution_case = self.prosecutor.build_case(crime_description)

        # Step 2: Defense responds
        defense_case = self.defense.build_case(crime_description)

        # Step 3: Cross-Examiner analyzes both sides
        cross_examination = self.cross_examiner.examine(prosecution_case, defense_case)

        # Step 4: Judge evaluates and renders verdict
        verdict = self.judge.render_verdict(prosecution_case, defense_case, cross_examination)

        # Compile full trial result
        trial_result = {
            "crime_description": crime_description,
            "prosecution": prosecution_case,
            "defense": defense_case,
            "cross_examination": cross_examination,
            "verdict": verdict
        }

        print("✅ Trial completed successfully.")
        return trial_result