from src.agent import ToTAgent


def test_tot_agent_selects_best_path():
    prompts = []

    def fake_llm(prompt: str) -> str:
        prompts.append(prompt)
        if "箇条書き" in prompt:
            return "- A\n- B"
        return "最終的な答え: done"

    def evaluate(history: str) -> float:
        return 1.0 if "B" in history else 0.0

    agent = ToTAgent(fake_llm, evaluate, max_depth=1, breadth=2)
    answer = agent.run("test")

    assert answer == "done"
    assert "B" in prompts[-1]
