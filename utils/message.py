import re


SENTENCE_END_RE = re.compile(r"[。！？!?；;]")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.S)


def split_chat_reply(text, max_parts=5, max_chars=180):
    if not isinstance(text, str):
        return []

    content = text.strip()
    if not content:
        return []

    parts = []
    segments = _split_code_blocks(content)
    for segment in segments:
        if segment.startswith("```") and segment.endswith("```"):
            parts.append(segment)
            continue

        for paragraph in re.split(r"\n+", segment):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            sentences = _split_paragraph(paragraph)
            for sentence in sentences:
                parts.extend(_split_long_sentence(sentence, max_chars))

    parts = [part for part in parts if part]
    if len(parts) <= max_parts:
        return parts

    head = parts[: max_parts - 1]
    tail = "".join(parts[max_parts - 1:]).strip()
    if tail:
        head.append(tail)
    return head


def _split_code_blocks(text):
    segments = []
    last_end = 0
    for match in CODE_BLOCK_RE.finditer(text):
        prefix = text[last_end:match.start()].strip()
        if prefix:
            segments.append(prefix)
        segments.append(match.group(0).strip())
        last_end = match.end()

    tail = text[last_end:].strip()
    if tail:
        segments.append(tail)

    return segments or [text.strip()]


def _split_paragraph(paragraph):
    sentences = []
    start = 0
    for match in SENTENCE_END_RE.finditer(paragraph):
        end = match.end()
        sentence = paragraph[start:end].strip()
        if sentence:
            sentences.append(sentence)
        start = end

    tail = paragraph[start:].strip()
    if tail:
        sentences.append(tail)

    return sentences


def _split_long_sentence(sentence, max_chars):
    if len(sentence) <= max_chars:
        return [sentence]

    return [sentence[index:index + max_chars] for index in range(0, len(sentence), max_chars)]
