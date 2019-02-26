def process_query(query_string, server):
    server.send_response(200)
    server.send_header('Content-type', 'text/html')
    server.end_headers()
    # now I can write.write to server

    opening_brace = "("
    closing_brace = ")"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    saved_words = [AND, OR, NOT]
    query_string = query_string.split("+")
    if query_string[0] == opening_brace:
        if query_string[1] == opening_brace:
            pass
            # case of two pairs of braces
    else:
        # case of one pair of braces
        pass

    operators = []
    words_to_look_for = []
    words_must_not_be_in_file = []

    # case of 0 braces
    if query_string[0] == NOT:
        words_must_not_be_in_file.append(query_string[1])
        if query_string[2] in saved_words:
            if query_string[3] == NOT:
                words_must_not_be_in_file.append(query_string[3])
            else:
                words_to_look_for.append(query_string[3])
            operators.append(AND)

    else:
        words_to_look_for.append(query_string[0])

    pass
