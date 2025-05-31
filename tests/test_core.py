# tests/test_core.py

from backend.core import CourtroomSimulator

def test_run_trial():
    simulator = CourtroomSimulator()
    crime_description = "A man caused grievous hurt with a weapon."

    result = simulator.run_trial(crime_description)

    assert result["prosecution"]["argument"], "Prosecution should return non-empty argument"
    assert result["defense"]["argument"], "Defense should return non-empty argument"
    assert result["cross_examination"]["questions"], "Cross-Examiner should ask questions"
    assert result["verdict"]["verdict"], "Judge should deliver a verdict"