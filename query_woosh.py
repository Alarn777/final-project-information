from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir


def find_woosh():

    ix = open_dir("indexdir")
    # query_str is query string
    query_str = "Computer OR Server"
    # Top 'n' documents as result
    topN = int("10")

    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(u"computer")

    with ix.searcher() as s:
        results = s.search(q)
        for i in results:
            print("test")
            print(i['title'])
            print(i['textdata'])
