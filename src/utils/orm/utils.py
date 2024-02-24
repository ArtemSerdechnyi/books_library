
def parse_int_or_none(value: str) -> int | None:
    try:
        return int(value.strip())
    except ValueError:
        return None
