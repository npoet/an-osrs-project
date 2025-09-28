def format_gp(value: int) -> str:
    """
    Formats GP values into OSRS-style notation.
    :param value: int value of items
    :return: formatted GP value string
    """
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B gp"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M gp"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K gp"
    else:
        return f"{value} gp"
