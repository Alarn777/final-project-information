#!/usr/bin/python
import collections
import timeit
import os
import pickle
import json

RECORD_TIME = False  # toggling for recording the time taken for indexer
BYTE_SIZE = 4  # docID is in int

"""
conducts boolean queries from queries_file and writes outputs to output_file
params:
    dictionary_file:    dictionary file produced by indexer
    postings_file:      postings file produced by indexer
    queries_file:       file of boolean queries
    output_file:        responses to boolean queries
"""


def search(query):
    # start time
    start = timeit.default_timer()

    # open files
    inverted_index_file = os.path.join(
        os.getcwd(), 'data', 'inverted_index.pickle')
    with open(inverted_index_file, mode='rb') as f:
        inverted_index = pickle.load(f)

    # load dictionary to memory
    dictionary = inverted_index.keys()

    # process query
    result = process_query(query, dictionary, inverted_index)
    print(result)

    # stop time
    RECORDED_TIME = timeit.default_timer() - start
    return result, RECORDED_TIME


"""
returns the list of docIDs in the result for the given query
params:
    query:          the query string e.g. 'bill OR Gates AND (vista OR XP) AND NOT mac'
    dictionary:     the dictionary in memory
    indexed_docIDs: the list of all docIDs indexed (used for negations)
"""


def process_query(query, dictionary, inverted_index):
    # prepare query list
    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query = query.split(' ')

    results_stack = []
    postfix_queue = collections.deque(shunting_yard(query))  # get query in postfix notation as a queue

    saved_queue = postfix_queue

    while postfix_queue:
        token = postfix_queue.popleft()
        result = []  # the evaluated result at each stage
        # if operand, add postings list for term to results stack
        if token != 'AND' and token != 'OR' and token != 'NOT':
            # default empty list if not in dictionary

            if token.replace("%22", "") in dictionary:
                result = load_result(token, inverted_index)

        # else if AND operator
        elif token == 'AND':
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'AND', left_operand) # check
            result = boolean_AND(left_operand, right_operand)  # evaluate AND

        # else if OR operator
        elif token == 'OR':
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            # print(left_operand, 'OR', left_operand) # check
            result = boolean_OR(left_operand, right_operand)  # evaluate OR

        # else if NOT operator
        elif token == 'NOT':
            right_operand = results_stack.pop()
            # print('NOT', right_operand) # check
            result = boolean_NOT(right_operand, inverted_index)  # evaluate NOT

        # push evaluated result back to stack
        results_stack.append(result)
        # print ('result', result) # check

    # NOTE: at this point results_stack should only have one item and it is the final result
    if len(results_stack) != 1: print("ERROR: results_stack. Please check valid query")  # check for errors

    res = results_stack.pop()

    data_path = os.path.abspath("./data")
    occurances_file = os.path.join(data_path, 'occurances_file.json')
    with open(occurances_file, "r") as read_file:
        occurances = json.load(read_file)
        bad_tokens = ['AND', 'OR', 'NOT', '(', ')']

        token_occurances = {}
        for file in res:

            token_occurances[file] = 0
            try:
                token_count = occurances[file]

            except:
                token_count = []

            for token in query:
                if token not in bad_tokens:
                    for val in token_count:
                        if token in val.keys():
                            token_occurances[file] += val[token]

        token_occurances_fixed = {}
        for tuple in token_occurances:
            token_occurances_fixed[os.path.basename(tuple)] = token_occurances[tuple]
            pass
        sorted_d = sorted((value, key) for (key, value) in token_occurances_fixed.items())
        print(sorted_d)

    return sorted_d


"""
returns posting list for term corresponding to the given offset
params:
    post_file:  opened postings file
    length:     length of posting list (same as df for the term)
    offset:     byte offset which acts as pointer to start of posting list in postings file
"""


def load_result(token, inverted_index):
    # open stop words and check
    data_path = os.path.abspath("./data")
    with open(data_path + "/" + "stopwords.json", 'r') as f:
        stopwords = json.load(f)

    result = None

    if token.replace("%22", "") not in stopwords["values"]:
        if result is None:
            result = inverted_index.get(token)
        else:
            result.intersection_update(inverted_index.get(token))

    elif token.replace("%22", "") in stopwords["values"] and "%22" in token:
        token = token.replace("%22", "")
        if result is None:
            result = inverted_index.get(token)
        else:
            result.intersection_update(inverted_index.get(token))
    else:
        return []

    # if result is None:
    #     result = inverted_index.get(token)
    # else:
    #     result.intersection_update(inverted_index.get(token))

    # clean up results
    cleaned_res = {''}
    cleaned_res.pop()
    if result:
        for val in result:
            val = os.path.basename(val)
            cleaned_res.add(val)

    return cleaned_res


"""
returns the list of postfix tokens converted from the given infix expression
params:
    infix_tokens: list of tokens in original query of infix notation
"""


def shunting_yard(infix_tokens):
    # define precedences
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')': 0}

    # declare data structures
    output = []
    operator_stack = []

    # while there are tokens to be read
    for token in infix_tokens:

        # if left bracket
        if token == '(':
            operator_stack.append(token)

        # if right bracket, pop all operators from operator stack onto output until we hit left bracket
        elif token == ')':
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()

        # if operator, pop operators from operator stack to queue if they are of higher precedence
        elif token in precedence:
            # if operator stack is not empty
            if operator_stack:
                current_operator = operator_stack[-1]
                while operator_stack and precedence[current_operator] > precedence[token]:
                    output.append(operator_stack.pop())
                    if operator_stack:
                        current_operator = operator_stack[-1]

            operator_stack.append(token)  # add token to stack

        # else if operands, add to output list
        else:
            output.append(token.lower())

    # while there are still operators on the stack, pop them into the queue
    while operator_stack:
        output.append(operator_stack.pop())
    # print ('postfix:', output)  # check
    return output


"""
returns the list of docIDs which is the compliment of given right_operand 
params:
    right_operand:  sorted list of docIDs to be complimented
    indexed_docIDs: sorted list of all docIDs indexed
"""


def boolean_NOT(right_operand, inverted_index):
    # creating U
    U = {''}
    U.remove('')
    for word in inverted_index:
        res = inverted_index.get(word)
        for i in res:
            U.add(os.path.basename(i))
    # complement of an empty list is list of all indexed (U)
    if not right_operand:
        return U

    result = []
    result = U - right_operand
    return result


"""
returns list of docIDs that results from 'OR' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""


def boolean_OR(left_operand, right_operand):
    # case if one of the operands are []
    if not left_operand:
        return right_operand
    if not right_operand:
        return left_operand

    result = []  # union of left and right operand
    result = left_operand | right_operand
    return result


"""
returns list of docIDs that results from 'AND' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""


def boolean_AND(left_operand, right_operand):
    # case if one of the operands are []
    if not left_operand:
        return []
    if not right_operand:
        return []

    # perform 'merge'
    result = []  # results list to be returned
    result = left_operand & right_operand
    return result


"""
prints the proper command usage
"""
#
# search("hello AND ( bla           OR           bla)          ")
