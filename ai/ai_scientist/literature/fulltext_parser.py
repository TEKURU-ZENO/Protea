"""Scientific manuscript full-text section parser."""

import re
from typing import Dict, List


class FullTextParser:
    """Parses scientific article text into standard IMRaD sections."""

    @staticmethod
    def parse_sections(text: str) -> Dict[str, str]:
        """Extract Introduction, Methods, Results, and Discussion sections."""
        sections = {
            "abstract": "",
            "introduction": "",
            "methods": "",
            "results": "",
            "discussion": "",
        }

        # Fallback simple partition
        lines = text.split("\n")
        current_section = "abstract"
        for line in lines:
            l_lower = line.lower().strip()
            if "introduction" in l_lower and len(l_lower) < 25:
                current_section = "introduction"
            elif any(k in l_lower for k in ["method", "experimental procedure"]) and len(l_lower) < 30:
                current_section = "methods"
            elif "result" in l_lower and len(l_lower) < 20:
                current_section = "results"
            elif any(k in l_lower for k in ["discussion", "conclusion"]) and len(l_lower) < 25:
                current_section = "discussion"
            else:
                sections[current_section] += line + " "

        return {k: v.strip() for k, v in sections.items()}
