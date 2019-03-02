import os
import re
import argparse
import pickle
import sys
from nltk.corpus import stopwords
import boolean

# Get inverted index from pickle file
inverted_index_file = os.path.join(
    os.getcwd(), 'data', 'inverted_index.pickle')

with open(inverted_index_file, mode='rb') as f:
    inverted_index = pickle.load(f)

dictionary = inverted_index.keys()

non_words = re.compile(r"[^A-Za-z'?]+")
stop_words = set(stopwords.words('english'))

# # Create a command line parser
# parser = argparse.ArgumentParser(description='Boolean query')
# parser.add_argument('query', help='words seperated by space')
# args = parser.parse_args()

# Preprocess query
query = "not hello and (wow and bla)"
algebra = boolean.BooleanAlgebra()
r = algebra.parse('not help and (together and foot)')
r = algebra.parse('not (together and foot)')
ad = r.get_literals()

print(r.objects)
results = []
for term in r.objects:
    query = term.lower()
    query = re.sub(non_words, ' ', query)
    words = {
        word for word in query.split()
        if word not in stop_words and word in dictionary}
    result = None
    if result is None:
        result = inverted_index.get(term)
    else:
        result.intersection_update(inverted_index.get(term))
    results.append(result)

# not has to be dealt with sepparetly as python doesn't support it on sets
j = r.pretty

# creating U
U = {''}
U.remove('')
for word in inverted_index:
    res = inverted_index.get(word)
    for i in res:
        U.add(i)

res = U - (results[1] | results[2])

query = query.lower()
query = re.sub(non_words, ' ', query)

# Remove all stopwords and words which is not in dictionary
words = {
    word for word in query.split()
    if word not in stop_words and word in dictionary}

result = None
for word in words:
    if result is None:
        result = inverted_index.get(word)
    else:
        result.intersection_update(inverted_index.get(word))

print(result)


def boolean_algebra():
    pass


def boolean_NOT(right_operand, indexed_docIDs):
    # Get inverted index from pickle file
    inverted_index_file = os.path.join(
        os.getcwd(), 'data', 'inverted_index.pickle')

    with open(inverted_index_file, mode='rb') as f:
        inverted_index = pickle.load(f)

    dictionary = inverted_index.keys()

    non_words = re.compile(r"[^A-Za-z'?]+")
    stop_words = set(stopwords.words('english'))

    # creating U
    U = {''}
    U.remove('')
    for word in inverted_index:
        res = inverted_index.get(word)
        for i in res:
            U.add(i)

    # getting the element
    query = right_operand
    query = query.lower()
    query = re.sub(non_words, ' ', query)

    # Remove all stopwords and words which is not in dictionary
    words = {
        word for word in query.split()
        if word not in stop_words and word in dictionary}

    result = None
    for word in words:
        if result is None:
            result = inverted_index.get(word)
        else:
            result.intersection_update(inverted_index.get(word))
    return result


"""
returns list of docIDs that results from 'OR' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""


def boolean_OR(left_operand, right_operand):
    query = left_operand
    term = ""
    query = re.sub(non_words, ' ', query)
    if query not in stop_words and query in dictionary:
       term = query
    result_left_operand = None
    if result_left_operand is None:
        result_left_operand = inverted_index.get(term)
    else:
        result_left_operand.intersection_update(inverted_index.get(term))

    query = right_operand
    term = ""
    query = re.sub(non_words, ' ', query)
    if query not in stop_words and query in dictionary:
        term = query
    result_right_operand = None
    if result_right_operand is None:
        result_right_operand = inverted_index.get(term)
    else:
        result_right_operand.intersection_update(inverted_index.get(term))

    return result_right_operand | result_left_operand


"""
returns list of docIDs that results from 'AND' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""


def boolean_AND(left_operand, right_operand):
    # perform 'merge'
    result = []  # results list to be returned
    l_index = 0  # current index in left_operand
    r_index = 0  # current index in right_operand
    l_skip = int(math.sqrt(len(left_operand)))  # skip pointer distance for l_index
    r_skip = int(math.sqrt(len(right_operand)))  # skip pointer distance for r_index

    while (l_index < len(left_operand) and r_index < len(right_operand)):
        l_item = left_operand[l_index]  # current item in left_operand
        r_item = right_operand[r_index]  # current item in right_operand

        # case 1: if match
        if (l_item == r_item):
            result.append(l_item)  # add to results
            l_index += 1  # advance left index
            r_index += 1  # advance right index

        # case 2: if left item is more than right item
        elif (l_item > r_item):
            # if r_index can be skipped (if new r_index is still within range and resulting item is <= left item)
            if (r_index + r_skip < len(right_operand)) and right_operand[r_index + r_skip] <= l_item:
                r_index += r_skip
            # else advance r_index by 1
            else:
                r_index += 1

        # case 3: if left item is less than right item
        else:
            # if l_index can be skipped (if new l_index is still within range and resulting item is <= right item)
            if (l_index + l_skip < len(left_operand)) and left_operand[l_index + l_skip] <= r_item:
                l_index += l_skip
            # else advance l_index by 1
            else:
                l_index += 1

    return result
