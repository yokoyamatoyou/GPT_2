import re
from typing import Callable, List, Tuple


class ToTAgent:
    """Minimal Tree-of-Thoughts style agent.

    The agent explores a search tree of candidate thought sequences.
    At each depth it expands the best nodes according to an evaluation
    function and finally asks the LLM to produce an answer based on the
    highest scoring path.
    """

    THOUGHT_RE = re.compile(r"^-\s*(.+)", re.MULTILINE)
    FINAL_RE = re.compile(r"^最終的な答え:\s*(.*)$", re.MULTILINE)

    def __init__(
        self,
        llm: Callable[[str], str],
        evaluate: Callable[[str], float],
        *,
        max_depth: int = 2,
        breadth: int = 2,
    ) -> None:
        """Create a new agent.

        Parameters
        ----------
        llm:
            Callable that takes a prompt and returns a completion.
        evaluate:
            Function scoring a history string, higher is better.
        max_depth:
            How many rounds of expansion to perform.
        breadth:
            How many candidates to keep at each depth.
        """
        self.llm = llm
        self.evaluate = evaluate
        self.max_depth = max_depth
        self.breadth = breadth

    def _propose(self, question: str, history: str) -> List[str]:
        """Ask the LLM for the next thought candidates."""
        prompt = (
            f"質問: {question}\n"
            f"これまでの思考:\n{history}\n"
            f"{self.breadth}個の次の思考候補を箇条書きで提案してください。"
        )
        output = self.llm(prompt)
        return [m.group(1).strip() for m in self.THOUGHT_RE.finditer(output)]

    def _final(self, question: str, history: str) -> str:
        """Request the final answer from the LLM."""
        prompt = f"質問: {question}\n思考過程:\n{history}\n最終的な答え:"
        resp = self.llm(prompt)
        match = self.FINAL_RE.search(resp)
        return match.group(1).strip() if match else resp.strip()

    def run(self, question: str) -> str:
        """Execute the search loop and return the final answer."""
        nodes: List[Tuple[str, float]] = [("", 0.0)]
        for _ in range(self.max_depth):
            candidates: List[Tuple[str, float]] = []
            for hist, _score in nodes:
                thoughts = self._propose(question, hist)
                for t in thoughts:
                    new_hist = (hist + "\n" + t) if hist else t
                    score = self.evaluate(new_hist)
                    candidates.append((new_hist, score))
            if not candidates:
                break
            candidates.sort(key=lambda x: x[1], reverse=True)
            nodes = candidates[: self.breadth]
        best_history = nodes[0][0]
        return self._final(question, best_history)
