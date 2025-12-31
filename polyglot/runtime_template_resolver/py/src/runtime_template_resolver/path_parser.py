from typing import List

def parse_path(path: str) -> List[str]:
    segments = []
    current = []
    in_bracket = False
    in_quote = None

    for char in path:
        if in_quote:
            if char == in_quote:
                in_quote = None
            else:
                current.append(char)
            continue

        if char == '"' or char == "'":
            in_quote = char
            continue

        if char == '[':
            if current:
                segments.append("".join(current))
                current = []
            in_bracket = True
            continue

        if char == ']':
            if current:
                segments.append("".join(current))
                current = []
            in_bracket = False
            continue

        if char == '.' and not in_bracket:
            if current:
                segments.append("".join(current))
                current = []
            continue

        current.append(char)

    if current:
        segments.append("".join(current))
    
    return segments
