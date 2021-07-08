def trim_quotes(string):
    # check if the string is surrounded by quotes
    if string[0] == '"' and string[-1] == '"':
        return string[1:-1]

    return string
