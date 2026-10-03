import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from searcher import Searcher


def load_test_questions(path: Path) -> list:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(searcher: Searcher, questions: list) -> dict:
    results = []
    correct_top1 = 0
    correct_top3 = 0
    above_threshold = 0

    for q in questions:
        search_results = searcher.search(q["question"], top_k=3)
        
        if not search_results:
            results.append({
                "question": q["question"],
                "top1_chunk": None,
                "top1_score": 0,
                "hit_top1": False,
                "hit_top3": False,
                "above_threshold": False,
            })
            continue

        top1 = search_results[0]
        top1_chunk = top1.payload["chunk_id"]
        top1_score = top1.score
        
        hit_top1 = top1_chunk == q["expected_chunk"]
        hit_top3 = any(
            point.payload["chunk_id"] == q["expected_chunk"]
            for point in search_results
        )
        above = top1_score >= q["min_score"]

        if hit_top1:
            correct_top1 += 1
        if hit_top3:
            correct_top3 += 1
        if above:
            above_threshold += 1

        results.append({
            "question": q["question"],
            "top1_chunk": top1_chunk,
            "top1_score": round(top1_score, 3),
            "hit_top1": hit_top1,
            "hit_top3": hit_top3,
            "above_threshold": above,
        })

    total = len(questions)
    return {
        "results": results,
        "metrics": {
            "accuracy_top1": correct_top1 / total,
            "accuracy_top3": correct_top3 / total,
            "above_threshold_rate": above_threshold / total,
            "total_questions": total,
        },
    }


def main():
    questions_path = Path(__file__).resolve().parent.parent / "data" / "test_questions.json"
    questions = load_test_questions(questions_path)
    
    searcher = Searcher()
    evaluation = evaluate(searcher, questions)

    print("\n=== РЕЗУЛЬТАТЫ ОЦЕНКИ ===\n")
    for r in evaluation["results"]:
        status = "✓" if r["hit_top1"] else "✗"
        print(f"{status} score {r['top1_score']:.3f} | {r['top1_chunk']} | {r['question']}")
    
    print("\n=== МЕТРИКИ ===")
    m = evaluation["metrics"]
    print(f"Accuracy@1: {m['accuracy_top1']:.1%} ({int(m['accuracy_top1'] * m['total_questions'])}/{m['total_questions']})")
    print(f"Accuracy@3: {m['accuracy_top3']:.1%} ({int(m['accuracy_top3'] * m['total_questions'])}/{m['total_questions']})")
    print(f"Above threshold: {m['above_threshold_rate']:.1%}")
    print(f"Total questions: {m['total_questions']}")

    out_path = Path(__file__).resolve().parent / "evaluation_results.json"
    out_path.write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nРезультаты сохранены: {out_path}")


if __name__ == "__main__":
    main()