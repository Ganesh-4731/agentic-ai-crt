def split_message(text: str, max_length: int = 4000) -> list[str]:
    """
    Split a long text string into chunks no longer than max_length characters.

    Splitting is performed only at newline boundaries to avoid breaking words
    or sentences mid-way. Each chunk is stripped of leading/trailing whitespace
    before being added to the result list.

    Args:
        text:       The full text to split.
        max_length: Maximum character length per chunk (default 4000, safe for
                    Telegram's 4096-char message limit).

    Returns:
        A list of strings. Usually 1–2 chunks for a typical travel blueprint.
    """
    if not text:
        return []

    if len(text) <= max_length:
        return [text.strip()]

    lines = text.splitlines(keepends=True)
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line)

        # Edge case: a single line is longer than max_length
        # (should not happen in normal blueprints, but handle gracefully)
        if line_length > max_length:
            # Flush current chunk first
            if current_chunk:
                chunks.append("".join(current_chunk).strip())
                current_chunk = []
                current_length = 0
            # Hard-split the oversized line by character
            for i in range(0, line_length, max_length):
                chunks.append(line[i : i + max_length].strip())
            continue

        if current_length + line_length > max_length:
            # Flush current chunk and start a new one
            chunks.append("".join(current_chunk).strip())
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    # Flush the final chunk
    if current_chunk:
        remainder = "".join(current_chunk).strip()
        if remainder:
            chunks.append(remainder)

    # Filter out any empty strings that may have crept in
    return [c for c in chunks if c]
