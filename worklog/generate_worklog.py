import argparse
from datetime import date
from pathlib import Path

INPUT_FILE = Path(__file__).with_name("worklog_input.txt")
DEFAULT_OUTPUT = Path(__file__).with_name("latest_worklog.txt")


def read_input(path: Path):
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    name = lines[0] if lines else "Your Name"
    tasks = []
    commits = []
    section = None
    for ln in lines[1:]:
        if not ln:
            continue
        lower = ln.lower()
        if lower == "[tasks]":
            section = "tasks"
            continue
        if lower == "[commits]":
            section = "commits"
            continue
        if section == "tasks":
            tasks.append(ln)
        elif section == "commits":
            commits.append(ln)
    return name, tasks, commits


def format_hours(hours: float) -> str:
    return f"{int(hours)}" if hours.is_integer() else f"{hours}"


def build_worklog(name, day, meeting_hours, tasks, commits):
    lines = [f"{name}'s Worklog - {day}"]
    lines.append(f"Team Meeting: {format_hours(meeting_hours)}h")
    lines.append("")  # blank line after meeting
    if tasks:
        lines.append("Task:")
        lines.extend(tasks)
        lines.append("")  # blank line after tasks
    if commits:
        lines.append("Commit Links:")
        lines.extend(commits)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a Teams-friendly worklog.")
    parser.add_argument(
        "meeting_hours",
        type=float,
        help="Meeting hours (e.g., 2 for 2h)",
    )
    parser.add_argument(
        "--input",
        default=str(INPUT_FILE),
        help="Path to input text file (default: worklog_input.txt beside this script)",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Where to save the worklog text (default: latest_worklog.txt beside this script)",
    )
    args = parser.parse_args()

    name, tasks, commits = read_input(Path(args.input))
    day = date.today().strftime("%B %d, %Y")
    text = build_worklog(name, day, args.meeting_hours, tasks, commits)

    output_path = Path(args.output).expanduser()
    output_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nSaved to {output_path.resolve()}")


if __name__ == "__main__":
    main()
