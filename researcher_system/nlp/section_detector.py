def detect_sections(text):
    sections={}
    parts=text.split("\n")
    current="general"
    for line in parts:
        if "introduction" in line.lower():
            current="introduction"
        if "method" in line.lower():
            current="method"
        sections.setdefault(current,"")
        sections[current]+=line+" "
    return sections
