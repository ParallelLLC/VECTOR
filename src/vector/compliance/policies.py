from typing import List
import re

class ComplianceError(Exception):
    pass

def assert_non_political(texts: List[str], deny_keywords: List[str]):
    joined = " ".join(texts).lower()
    for kw in deny_keywords:
        if re.search(r"\b"+re.escape(kw.lower())+r"\b", joined):
            raise ComplianceError(f"Disallowed political targeting keyword detected: '{kw}'")
