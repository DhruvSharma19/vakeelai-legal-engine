"""
Indian Number & Currency to Words Converter
-------------------------------------------
Converts monetary sums and integers into formal words according to the Indian
numbering system (Lakhs and Crores), as required in standard Indian court pleadings
(e.g., "Rs. 25,00,000/- (Rupees Twenty-Five Lakh Only)").
Pure Python implementation; zero external dependencies.
"""

def number_to_indian_words(n: int) -> str:
    """Converts a positive integer into words using Indian numbering conventions."""
    if n == 0:
        return "Zero"

    ones = [
        "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"
    ]
    tens = [
        "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
    ]

    def _two_digits(val: int) -> str:
        if val < 20:
            return ones[val]
        else:
            t = tens[val // 10]
            o = ones[val % 10]
            return f"{t} {o}".strip() if o else t

    def _three_digits(val: int) -> str:
        h = val // 100
        rest = val % 100
        parts = []
        if h > 0:
            parts.append(f"{ones[h]} Hundred")
        if rest > 0:
            if h > 0:
                parts.append("and")
            parts.append(_two_digits(rest))
        return " ".join(parts)

    parts = []
    # Crores (1,00,00,000)
    crores = n // 10000000
    n %= 10000000
    if crores > 0:
        parts.append(f"{_three_digits(crores)} Crore")

    # Lakhs (1,00,000)
    lakhs = n // 100000
    n %= 100000
    if lakhs > 0:
        parts.append(f"{_two_digits(lakhs)} Lakh")

    # Thousands (1,000)
    thousands = n // 1000
    n %= 1000
    if thousands > 0:
        parts.append(f"{_two_digits(thousands)} Thousand")

    # Remaining hundreds/tens/ones
    if n > 0:
        parts.append(_three_digits(n))

    return " ".join(parts).strip()


def format_indian_currency(amount: float) -> str:
    """
    Formats a floating-point or integer number into Indian currency format:
    e.g. 2350000.50 -> 'Rs. 23,50,000.50/- (Rupees Twenty-Three Lakh Fifty Thousand and Fifty Paise Only)'
    """
    int_part = int(abs(amount))
    paise = int(round((abs(amount) - int_part) * 100))

    # Format numbers with Indian commas: xx,xx,xxx
    s = str(int_part)
    if len(s) <= 3:
        formatted_num = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_num = ",".join(groups) + "," + last3

    words = f"Rupees {number_to_indian_words(int_part)}"
    if paise > 0:
        words += f" and {number_to_indian_words(paise)} Paise"
    words += " Only"

    paise_str = f".{paise:02d}" if paise > 0 else ""
    return f"Rs. {formatted_num}{paise_str}/- ({words})"
