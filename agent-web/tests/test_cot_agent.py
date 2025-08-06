from modules.agents import CoTAgent

class MockLLMClient:
    def __init__(self, responses):
        self.responses = responses

    def chat(self, messages, stream=False):
        if not self.responses:
            return "最終的な答え: ran out of responses"
        return self.responses.pop(0)

def test_cot_agent_returns_final_answer():
    responses = [
        "思考: intermediate",
        "最終的な答え: done",
    ]
    mock_client = MockLLMClient(responses)
    agent = CoTAgent(mock_client)
    answer = agent.run("質問")
    assert answer == "done"


def test_cot_run_iter_yields_steps():
    responses = [
        "思考: step",
        "最終的な答え: ok",
    ]
    mock_client = MockLLMClient(responses)
    agent = CoTAgent(mock_client)
    steps = list(agent.run_iter("q"))
    assert steps[0].startswith("思考")
    assert steps[1].startswith("最終的な答え")
    assert steps[2] == "ok"
