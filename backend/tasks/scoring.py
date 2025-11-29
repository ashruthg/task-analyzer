"""
Standalone scoring module. This is the working core of the submission.

Functions:
- parse_date_safe
- calculate_task_score
- analyze_tasks
- suggest_top_tasks

These functions operate on Python dictionaries and require no Django.
"""
from datetime import datetime, date
from dateutil import parser
from typing import List, Dict, Any, Tuple, Set

# --- Configuration weights (tweakable) ---
IMPORTANCE_WEIGHT = 6
URGency_OVERDUE_BOOST = 120
URGENCY_SOON_BOOST = 40
QUICK_WIN_BONUS = 12
DEPENDENCY_BONUS = 15


def parse_date_safe(date_str: str) -> date:
    try:
        return parser.parse(date_str).date()
    except Exception:
        # If parsing fails, return a far future date
        return date(9999, 12, 31)


def days_until(due: date) -> int:
    today = date.today()
    return (due - today).days


def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> Set[int]:
    """
    Simple detection of circular dependencies; returns IDs involved in cycles.
    Note: tasks are expected as dicts with an implicit index ID (their list index).
    """
    n = len(tasks)
    graph = {i: set(tasks[i].get('dependencies', [])) for i in range(n)}

    visited = [0] * n
    in_cycle = set()

    def dfs(u, stack):
        if visited[u] == 1:
            if u in stack:
                idx = stack.index(u)
                cycle_nodes = stack[idx:]
                for c in cycle_nodes:
                    in_cycle.add(c)
            return
        if visited[u] == 2:
            return

        visited[u] = 1
        stack.append(u)
        for v in graph.get(u, []):
            if 0 <= v < n:
                dfs(v, stack)
        stack.pop()
        visited[u] = 2

    for i in range(n):
        if visited[i] == 0:
            dfs(i, [])

    return in_cycle


def calculate_task_score(task: Dict[str, Any], all_tasks: List[Dict[str, Any]], idx: int, circular_set: Set[int]) -> Tuple[float, str]:
    """Calculate score for a single task and return (score, explanation)."""
    explanation = []
    score = 0.0

    # Safe extraction
    title = task.get('title', 'Untitled')
    due_date_raw = task.get('due_date')
    importance = int(task.get('importance', 5) or 5)
    est_hours = int(task.get('estimated_hours', 1) or 1)
    dependencies = task.get('dependencies', []) or []

    # Parse date
    due = parse_date_safe(due_date_raw) if due_date_raw else date(9999, 12, 31)
    days = days_until(due)

    # Urgency
    if days < 0:
        score += URGency_OVERDUE_BOOST
        explanation.append(f"Overdue by {-days} days: +{URGency_OVERDUE_BOOST}")
    elif days <= 3:
        score += URGENCY_SOON_BOOST
        explanation.append(f"Due in {days} days: +{URGENCY_SOON_BOOST}")
    else:
        val = max(0, (10 - min(days, 10)))
        score += val
        explanation.append(f"Due in {days} days: +{val}")

    # Importance
    imp_add = importance * IMPORTANCE_WEIGHT
    score += imp_add
    explanation.append(f"Importance {importance}: +{imp_add}")

    # Effort (quick wins)
    if est_hours <= 2:
        score += QUICK_WIN_BONUS
        explanation.append(f"Quick win (<=2h): +{QUICK_WIN_BONUS}")
    else:
        pen = max(0, (est_hours - 2) * 1.5)
        score -= pen
        explanation.append(f"High effort ({est_hours}h): -{pen:.1f}")

    # Dependency: if others depend on this task
    dependents = 0
    for t in all_tasks:
        deps = t.get('dependencies', []) or []
        if idx in deps:
            dependents += 1

    if dependents > 0:
        dep_add = DEPENDENCY_BONUS * dependents
        score += dep_add
        explanation.append(f"Has {dependents} dependent(s): +{dep_add}")

    # Circular dependency penalty
    if idx in circular_set:
        score -= 10
        explanation.append("In circular dependency: -10")

    return score, "; ".join(explanation)


def analyze_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return tasks sorted by score (desc), with score + explanation added."""
    circular_set = detect_circular_dependencies(tasks)

    results = []
    for i, t in enumerate(tasks):
        score, expl = calculate_task_score(t, tasks, i, circular_set)
        out = dict(t)
        out['__score'] = round(score, 2)
        out['__explanation'] = expl
        results.append(out)

    results.sort(key=lambda x: x['__score'], reverse=True)
    return results


def suggest_top_tasks(tasks: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
    analyzed = analyze_tasks(tasks)
    top = analyzed[:top_n]
    return [
        {
            'title': t.get('title', 'Untitled'),
            'score': t['__score'],
            'explanation': t['__explanation']
        }
        for t in top
    ]


# Demo run
if __name__ == '__main__':
    sample = [
        {"title": "Fix login bug", "due_date": "2025-11-30", "estimated_hours": 3, "importance": 8, "dependencies": []},
        {"title": "Write README", "due_date": "2025-12-02", "estimated_hours": 1, "importance": 6, "dependencies": [0]},
        {"title": "Hotfix payment", "due_date": "2025-11-25", "estimated_hours": 4, "importance": 9, "dependencies": []}
    ]
    print(analyze_tasks(sample))
