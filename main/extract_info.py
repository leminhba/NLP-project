

def find_sections(splitter, text):
    starts = [match.span()[0] for match in splitter.finditer(text)] + [len(text)]
    sections = [text[starts[idx]:starts[idx+1]] for idx in range(len(starts)-1)]
    return sections
def extract_2section(splitter1, splitter2, text):
    found = False
    sections = find_sections(splitter1, text)
    section_info_list = []

    sections_content = ''
    for section in sections:
        section_lines = section.splitlines()
        section_head = section_lines[0]
        sections_content = "\n".join(section_lines[1:])
        sections_numeric = find_sections(splitter2, sections_content)
        section_info_list.append((section_head, None))
        for section_numeric in sections_numeric:
            section_head_numeric = section_numeric.splitlines()[0]
            section_numeric_content = "\n".join(section_numeric.splitlines()[1:])
            section_info_list.append((section_head_numeric, section_numeric_content))

        found = True
    return section_info_list, found

def extract_section(splitter, text):
    found = False
    sections = find_sections(splitter, text)
    section_info_list = []
    sections_content = ''
    for section in sections:
        section_lines = section.splitlines()
        section_head = section_lines[0]
        sections_content = "\n".join(section_lines[1:])
        section_info_list.append((section_head, sections_content))
        found = True
    return section_info_list, found