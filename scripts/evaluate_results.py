"""
Lab 6 CineSense – Evaluation Script
Analyzes prompt outputs and calculates metrics
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path("outputs")
EVAL_DIR = Path("eval")


def evaluate_output(row: dict) -> dict:
    """
    Evaluate one LLM output against gold standard.
    
    Returns dict with error categories and metrics.
    """
    review_id = row["review_id"]
    gold_sentiment = row["gold_sentiment"].strip().lower()
    pred_sentiment = row["pred_sentiment"].strip().lower() if row["pred_sentiment"] else ""
    valid_json = int(row["valid_json"])
    llm_output = row["llm_output"]
    review_text = row["review_text"].lower()

    errors = []
    
    # Check if invalid JSON
    if not valid_json:
        errors.append("invalid_json")
        return {
            "review_id": review_id,
            "gold_sentiment": gold_sentiment,
            "pred_sentiment": pred_sentiment if pred_sentiment else "N/A",
            "accuracy": 0,
            "valid_json": 0,
            "primary_error": "invalid_json",
            "error_count": 1,
        }

    # Parse the JSON
    try:
        parsed = json.loads(llm_output)
    except:
        errors.append("invalid_json")
        return {
            "review_id": review_id,
            "gold_sentiment": gold_sentiment,
            "pred_sentiment": pred_sentiment if pred_sentiment else "N/A",
            "accuracy": 0,
            "valid_json": 0,
            "primary_error": "invalid_json",
            "error_count": 1,
        }

    # Check sentiment accuracy
    accuracy = 1 if pred_sentiment == gold_sentiment else 0
    if accuracy == 0:
        errors.append("wrong_sentiment")

    # Check for hallucination
    if "evidence_phrases" in parsed and isinstance(parsed["evidence_phrases"], list):
        for phrase in parsed["evidence_phrases"]:
            if phrase.lower() not in review_text and phrase not in row["review_text"]:
                errors.append("hallucinated_evidence")
                break

    # Check confidence for mixed/ambiguous reviews
    difficulty = ""
    if "difficulty" in row:
        difficulty = row.get("review_type", "").lower()
    
    if "confidence" in parsed:
        conf = str(parsed["confidence"]).lower()
        if "mixed" in difficulty or "ambiguous" in difficulty:
            if conf == "high":
                errors.append("overconfident")

    # Check for keyword traps
    if "keyword_trap" in difficulty:
        # These reviews have positive surface words but negative overall sentiment
        if gold_sentiment == "negative" and pred_sentiment == "positive":
            errors.append("keyword_trap")

    primary_error = errors[0] if errors else "none"

    return {
        "review_id": review_id,
        "gold_sentiment": gold_sentiment,
        "pred_sentiment": pred_sentiment,
        "accuracy": accuracy,
        "valid_json": valid_json,
        "primary_error": primary_error,
        "error_count": len(errors),
    }


def evaluate_results(prompt_version: str):
    """
    Evaluate all outputs for one prompt version.
    """
    result_file = OUTPUT_DIR / f"result_{prompt_version}.csv"
    eval_file = EVAL_DIR / f"eval_{prompt_version}.csv"
    
    EVAL_DIR.mkdir(exist_ok=True)

    rows = []
    with result_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    evaluations = []
    for row in rows:
        eval_result = evaluate_output(row)
        evaluations.append(eval_result)

    # Write evaluation file
    with eval_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "review_id",
                "gold_sentiment",
                "pred_sentiment",
                "accuracy",
                "valid_json",
                "primary_error",
                "error_count",
            ],
        )
        writer.writeheader()
        writer.writerows(evaluations)

    # Calculate metrics
    total = len(evaluations)
    correct = sum(e["accuracy"] for e in evaluations)
    valid_json_count = sum(e["valid_json"] for e in evaluations)
    
    accuracy = correct / total if total > 0 else 0
    valid_json_rate = valid_json_count / total if total > 0 else 0

    # Count error buckets
    error_counts = defaultdict(int)
    for e in evaluations:
        if e["primary_error"] != "none":
            error_counts[e["primary_error"]] += 1

    return {
        "prompt_version": prompt_version,
        "total_reviews": total,
        "accuracy": accuracy,
        "valid_json_rate": valid_json_rate,
        "error_buckets": dict(error_counts),
        "evaluations": evaluations,
    }


def main():
    print("\n=== Lab 6 CineSense Evaluation ===\n")

    all_results = {}
    
    for prompt_version in ["v1", "v2", "v3_cot"]:
        print(f"Evaluating Prompt {prompt_version}...")
        result = evaluate_results(prompt_version)
        all_results[prompt_version] = result
        
        print(f"  Accuracy: {result['accuracy']:.1%}")
        print(f"  Valid JSON Rate: {result['valid_json_rate']:.1%}")
        print(f"  Error Buckets: {result['error_buckets']}")
        print()

    # Print comparison table
    print("\n=== Quantitative Comparison ===\n")
    print(f"{'Metric':<30} {'Prompt v1':<15} {'Prompt v2':<15} {'Prompt v3 CoT':<15}")
    print("-" * 75)
    
    print(f"{'Accuracy':<30} {all_results['v1']['accuracy']:.1%}{'':11} {all_results['v2']['accuracy']:.1%}{'':11} {all_results['v3_cot']['accuracy']:.1%}")
    print(f"{'Valid JSON Rate':<30} {all_results['v1']['valid_json_rate']:.1%}{'':11} {all_results['v2']['valid_json_rate']:.1%}{'':11} {all_results['v3_cot']['valid_json_rate']:.1%}")
    
    print("\n✓ Evaluation complete!")
    print(f"Results saved to: {EVAL_DIR}/")


if __name__ == "__main__":
    main()
