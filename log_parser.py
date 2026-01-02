import re

def extract_error_blocks(log_text, max_lines=300):
    """
    Extract likely error or exception blocks from Tomcat logs.
    """
    lines = log_text.splitlines()
    error_lines = []
    capture = False
    count = 0

    for line in lines:
        if re.search(r"(SEVERE|Exception|ERROR|Caused by|^\tat )", line):
            capture = True
            count = 0
        if capture:
            error_lines.append(line)
            count += 1
        if capture and count > max_lines:
            capture = False
            count = 0

    return "\n".join(error_lines)
