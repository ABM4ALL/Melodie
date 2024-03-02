def first_char_upper(s: str) -> str:
    if len(s) >= 1:
        return s[0].upper() + s[1:]
    else:
        return s


def underline_to_camel(s):
    return "".join(first_char_upper(word) for word in s.split("_"))
