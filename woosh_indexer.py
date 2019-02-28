from whoosh.fields import Schema, TEXT
import os, os.path
from whoosh import index

import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import sys


def createSearchableData(root):
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True),
                    content=TEXT, textdata=TEXT(stored=True))
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    # Creating a index writer to add document as per schema
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    for path in filepaths:
        if path == "corpus/.DS_Store":
            continue
        fp = open(path, 'r')
        print(path)
        text = fp.read()

        file_name = path
        file_name = file_name.replace(".txt", "")
        file_name = file_name.replace("corpus/", "")
        writer.add_document(title=file_name, path=path,
                            content=text, textdata=text)
        fp.close()
    writer.commit()


def index_woosh():
    root = "corpus"
    createSearchableData(root)
    # schema = Schema(title=TEXT, content=TEXT)
    #
    # if not os.path.exists("indexdir"):
    #     os.mkdir("indexdir")
    #
    # ix = index.create_in("indexdir", schema)
    #
    #
    #
    #
    # ix = index.open_dir("indexdir")
    # writer = ix.writer()
    #
    # writer.add_document(title=u"My document", content=u"This is my document!")
    # writer.add_document(title=u"Second try", content=u"This is the second example.")
    # writer.add_document(title=u"Third time's the charm", content=u"Examples are many.")
    # writer.commit()
