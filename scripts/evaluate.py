"""Execute synthetic scenarios against real local tools; no remote API calls."""

import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import personal_ai_assistant.models  # noqa: F401
from personal_ai_assistant.assistant import demo_chat
from personal_ai_assistant.db import Base


def evaluate():
    scenarios = json.loads((Path(__file__).parents[1] / "evals/scenarios.json").read_text())
    results = []
    for scenario in scenarios:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(engine)
        with sessionmaker(engine)() as db:
            output = demo_chat(db, scenario["input"])
        actual_tool = (
            output["tool_results"][0].get("tool")
            or output["tool_results"][0].get("proposed_action")
            if output["tool_results"]
            else None
        )
        result = {
            "id": scenario["id"],
            "expected": scenario["status"],
            "actual": output["status"],
            "pass": output["status"] == scenario["status"] and actual_tool == scenario["tool"],
        }
        results.append(result)
        engine.dispose()
    passed = sum(item["pass"] for item in results)
    print(json.dumps({"passed": passed, "total": len(results), "scenarios": results}, indent=2))
    return passed == len(results)


if __name__ == "__main__":
    raise SystemExit(0 if evaluate() else 1)
