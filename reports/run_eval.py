import json
from typing import Any, List
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import fire
from tqdm import tqdm

from holosophos.main_agent import run_main_agent


@dataclass
class AgentTask:
    query: str
    model_name: str
    task_id: int
    target: List[str]


def run_eval(
    input_path: str,
    model_name: str = "gpt-4o-mini",
    max_workers: int = 1,
    verbosity_level: int = 2,
):
    with open(input_path) as f:
        records = [json.loads(line) for line in f]
    tasks = [AgentTask(
        query=r["query"],
        target=r["target"],
        model_name=model_name,
        task_id=i
    ) for i, r in enumerate(records)]

    def worker(task: AgentTask) -> Any:
        answer = run_main_agent(
            query=task.query,
            model_name=task.model_name,
            verbosity_level=verbosity_level
        )
        print(f"TARGET: {task.target}\nPREDICTED: {answer}")
        return answer

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(worker, tasks), total=len(tasks), desc="Processing queries", unit="query"))

    correct_count = 0
    for record, result in zip(records, results):
        query = record["query"]
        target = record["target"]
        is_correct = False
        for arxiv_id in target:
            if arxiv_id in result:
                is_correct = True
        correct_count += int(is_correct)
        print(f"Query: {query}\nTarget: {target}\nPrediction: {result}\nLabel: {is_correct}\n\n")
    print(f"Overall accuracy: {correct_count / len(records) * 100.0:.1f}")


if __name__ == "__main__":
    fire.Fire(run_eval)
