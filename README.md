# Smart Task Analyzer


**Status:** Standalone scoring module + frontend demo. Django project structure provided as placeholders (non-running).


## What this submission includes


- A working Python scoring function: `backend/tasks/scoring.py` — can be run without Django.
- Frontend demo (`frontend/index.html`, `frontend/script.js`, `frontend/styles.css`) that accepts tasks and displays sorted results using the scoring logic via a mock fetch.
- Placeholder Django project structure in `backend/` to show how this would be integrated in a full implementation.
- Unit tests for the scoring logic (`backend/tasks/tests.py`).


## Why this approach


I have limited experience with Django and could not complete full backend integration reliably within the timeframe. To demonstrate problem-solving, algorithmic thinking, and frontend integration, I implemented:


- A clear, documented priority scoring function that handles edge cases (missing fields, invalid dates, overdue tasks, circular dependency detection heuristics).
- A responsive frontend to visualize results and explanations for each task's score.


I documented assumptions and design decisions below.


## How to run the scoring function locally (no Django needed)


1. Ensure Python 3.8+ is installed.
2. From the repository root, create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate # macOS / Linux
venv\Scripts\activate # Windows
```
3. Install dependencies (only for tests):

```
pip install -r requirements.txt
```
Run the sample script to test scoring (standalone):
```
python -c "from backend.tasks.scoring import analyze_tasks; print(analyze_tasks([{'title':'Test','due_date':'2025-12-01','importance':8,'estimated_hours':2,'dependencies':[]}]))"
```

How to view the frontend demo

Open frontend/index.html in your browser (double-click or open it).

Paste a JSON array of tasks (example provided in the UI) or add tasks in the form.

Click "Analyze" to see the sorted results and explanations. The frontend calls a mock function that uses the same scoring logic shipped in scoring.py.
