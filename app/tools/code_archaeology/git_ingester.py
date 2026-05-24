"""
git_ingester.py  v4
-------------------
Parses the full git history of a repository and returns rich, structured
commit data.  Two backends: GitPython → subprocess fallback.

New in v4
─────────
• CoChangeMatrix   — files that frequently change together (coupling heatmap)
• KnowledgeSilo    — per-author exclusive ownership score (bus-factor proxy)
• RefactorTrend    — conventional-commit type distribution over rolling windows
• VelocityMetrics  — adds stddev, acceleration (Δcommits/day between windows),
                     and momentum (EMA of weekly commit counts)
• GlossaryEntry    — symbol/acronym extraction from commit subjects + bodies
• Everything from v3 is preserved and extended (no regressions)
"""

from __future__ import annotations

import re
import json
import math
import subprocess
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from itertools import combinations
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

# (rest of file omitted in package - original logic kept)

__all__ = []
