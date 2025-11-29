"""
Simple Task model placeholder.
This is intentionally not using django.db models to avoid import/runtime issues.
"""


from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskObj:
title: str
due_date: str # ISO date string
importance: int = 5
estimated_hours: int = 1
dependencies: List[int] = field(default_factory=list)


def to_dict(self):
return {
'title': self.title,
'due_date': self.due_date,
'importance': self.importance,
'estimated_hours': self.estimated_hours,
'dependencies': self.dependencies,
}