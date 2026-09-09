import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT10 = Path(__file__).resolve().parent.parent / "10-multi-agent-orchestration"
sys.path.insert(0, str(PROJECT10))
os.chdir(PROJECT10)

from dotenv import load_dotenv
load_dotenv(PROJECT10 / ".env")

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ANTHROPIC_API_KEY isn't set (checked 10-multi-agent-orchestration/.env).")
    sys.exit(1)

from src.orchestrator import route

CASES_PATH = Path(__file__).resolve().parent / "eval_cases.json"


def score_case(case: dict, result: dict) -> dict:
    domain_ok = result["domain"] == case["expected_domain"]
    answer_lower = result["answer"].lower()
    missing = [kw for kw in case["must_contain"] if kw.lower() not in answer_lower]
    return {
        "id": case["id"],
        "actual_domain": result["domain"],
        "domain_ok": domain_ok,
        "missing_keywords": missing,
        "passed": domain_ok and not missing,
    }


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        print(f"Running {case['id']}: {case['question']!r}")
        try:
            result = route(case["question"])
        except Exception as e:
            results.append({"id": case["id"], "actual_domain": "ERROR", "domain_ok": False,
                             "missing_keywords": ["<error>"], "passed": False})
            print(f"  ERROR: {e}")
            continue
        r = score_case(case, result)
        results.append(r)
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] domain={r['actual_domain']} (expected {case['expected_domain']})"
              + ("" if r["domain_ok"] and not r["missing_keywords"] else f"  missing={r['missing_keywords']}"))

    passed = sum(1 for r in results if r["passed"])
    print(f"\n=== {passed}/{len(results)} passed ===")

    by_domain: dict[str, list] = {}
    for case, r in zip(cases, results):
        by_domain.setdefault(case["expected_domain"], []).append(r["passed"])
    for domain, outcomes in by_domain.items():
        print(f"  {domain}: {sum(outcomes)}/{len(outcomes)}")

    report_dir = Path(__file__).resolve().parent / "eval_reports"
    report_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = report_dir / f"{timestamp}.json"
    report_path.write_text(json.dumps({
        "timestamp": timestamp, "passed": passed, "total": len(results),
        "by_domain": {d: {"passed": sum(o), "total": len(o)} for d, o in by_domain.items()},
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"\nSaved report to {report_path}")


if __name__ == "__main__":
    main()