def calculate_cagr(start, end, years):
    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:
        return ((end/start)**(1/years) - 1)*100, "NORMAL"

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "UNKNOWN"