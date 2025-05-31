# tests/test_agents.py

from backend.agents.prosecution_agent import ProsecutionAgent
from backend.agents.defense_agent import DefenseAgent
from backend.agents.judge_agent import JudgeAgent

def test_prosecution_agent():
    agent = ProsecutionAgent()
    result = agent.build_case("A man stabbed another during an argument.")
    
    assert "argument" in result, "Prosecution should return an argument"
    assert len(result["retrieved_sections"]) > 0, "Should retrieve at least one IPC section"


def test_defense_agent():
    agent = DefenseAgent()
    result = agent.build_case("A man stabbed another during an argument.")
    
    assert "argument" in result, "Defense should return an argument"
    assert len(result["retrieved_sections"]) > 0, "Should retrieve at least one defense-related section"


def test_judge_agent():
    from backend.agents.prosecution_agent import ProsecutionAgent
    from backend.agents.defense_agent import DefenseAgent
    from backend.agents.cross_examiner_agent import CrossExaminerAgent

    p = ProsecutionAgent().build_case("A man stabbed another during an argument.")
    d = DefenseAgent().build_case("A man stabbed another during an argument.")
    x = CrossExaminerAgent().examine(p, d)

    judge = JudgeAgent()
    verdict = judge.render_verdict(p, d, x)

    assert "verdict" in verdict, "Judge should render a verdict"
    assert len(verdict["retrieved_sections"]) > 0, "Verdict should cite legal sections"