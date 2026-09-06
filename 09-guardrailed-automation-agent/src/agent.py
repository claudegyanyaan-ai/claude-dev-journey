"""CLI that ties extract -> guardrail -> store together for one or more
inquiry emails.

Auto-writes to the enrollment spreadsheet when guardrail.evaluate() says
it's safe to; otherwise shows the extracted lead and the reason(s) it's
pausing, and asks for an explicit human decision before writing anything.
This interactive pause is the whole point of Project 9 -- guardrail.py
decides WHEN to pause, agent.py is what actually pauses.
"""

import sys
import argparse

import extract
import guardrail
import store


def confirm(prompt):
    """Ask a yes/no question on the terminal. Defaults to No on blank/EOF.

    Defaulting to No (rather than crashing, or defaulting to Yes) matches
    the project's whole "never act on an uncertain case" discipline --
    an unanswered or unparseable response should never write data.
    """
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def process_email(path, spreadsheet_path=store.DEFAULT_PATH):
    """Run one email file through extract -> guardrail -> store.

    Returns True if a row was written (auto or after confirmation), False
    otherwise -- lets main() report an accurate summary across multiple
    files. spreadsheet_path defaults to the real enrollment sheet but is
    overridable so tests can point it at a throwaway temp file instead.
    """
    print(f"\n=== {path} ===")

    lead = extract.extract_from_file(path)
    if lead is None:
        print("Could not extract a lead from this email -- skipping.")
        return False

    print("Extracted:")
    for field in extract.FIELDS:
        print(f"  {field}: {lead[field]!r}")

    existing_rows = store.load_rows(spreadsheet_path)
    result = guardrail.evaluate(lead, existing_rows)

    if result["decision"] == "auto_write":
        store.append_row(lead, path=spreadsheet_path)
        print("-> Auto-written to the enrollment spreadsheet.")
        return True

    print("-> Needs confirmation:")
    for reason in result["reasons"]:
        print(f"     - {reason}")

    if confirm("Write this row anyway?"):
        store.append_row(lead, path=spreadsheet_path)
        print("-> Written (after confirmation).")
        return True

    print("-> Skipped. Nothing written.")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract a lead from one or more inquiry emails and add "
                     "it to the enrollment spreadsheet, pausing for "
                     "confirmation whenever the data looks incomplete or "
                     "implausible."
    )
    parser.add_argument("email_files", nargs="+", help="One or more .txt email files.")
    args = parser.parse_args()

    written = 0
    for path in args.email_files:
        if process_email(path):
            written += 1

    print(f"\n{written}/{len(args.email_files)} email(s) written to the spreadsheet.")


if __name__ == "__main__":
    main()
