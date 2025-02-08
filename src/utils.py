import re

def remove_headers_footers(text, header_patterns=None, footer_patterns=None):
    if header_patterns is None:
        header_patterns = [r'^.*Header.*$']
    if footer_patterns is None:
        footer_patterns = [r'^.*Footer.*$']

    for pattern in header_patterns + footer_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)

    return text.strip()

def remove_special_characters(text, special_chars=None):
    if special_chars is None:
        special_chars = r'[^A-Za-z0-9\s\.,;:\'\"\?\!\-]'

    text = re.sub(special_chars, '', text)
    return text.strip()

def remove_repeated_substrings(text, pattern=r'\.{2,}'):
    text = re.sub(pattern, '.', text)
    return text.strip()

def remove_extra_spaces(text):
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def preprocess_text(text):
    # Remove headers and footers
    text = remove_headers_footers(text)

    # Remove special characters
    text = remove_special_characters(text)

    # Remove repeated substrings like dots
    text = remove_repeated_substrings(text)

    # Remove extra spaces between lines and within lines
    text = remove_extra_spaces(text)

    # Additional cleaning steps can be added here

    return text.strip()

def get_questions_distribution(nb_text_chunks, nb_questions):
    index = 0
    questions_distribution = [0 for i in range(nb_text_chunks)]
    for _ in range(nb_questions):
        questions_distribution[index] += 1
        index = (index + 1) % nb_text_chunks
    return questions_distribution