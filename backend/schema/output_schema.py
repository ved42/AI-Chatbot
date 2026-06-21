from __future__ import annotations

from pydantic import BaseModel
from typing import List


class HealthResponse(BaseModel):
    status: str
    database: str
