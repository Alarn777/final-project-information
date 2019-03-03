import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import cgi
import re
from json import JSONDecodeError
from os import curdir, sep
import os
import search
import acive_passive_files
from index import do_index
from spider import run_spider

hostName = "localhost"
hostPort = 9000

PORT_NUMBER = 8080


class myHandler(BaseHTTPRequestHandler):
    last_query = ""

    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)

    def cleaning2(self, text):
        text = re.sub(r'\b(?:(?:https?|ftp)://)?\w[\w-]*(?:\.[\w-]+)+\S*', ' ', text.lower())
        words = re.findall(r'[a-z]+', text)
        return ' '.join(words)

    # search_array = []
    # have_parameters = False

    # Handler for the POST requests
    def do_POST(self):
        if self.path == "/send":
            # with open(curdir + sep + filename, 'r') as f:
            #     datastore = json.load(f)
            # if "words" in datastore:
            #     if "Carol" in datastore["words"]:
            #         print(datastore["words"]["Carol"])

            return

    # Handler for the GET requests

    def do_GET(self):
        docs_path = os.path.abspath("./docs")
        data_path = os.path.abspath("./data")

        # admin panel
        if self.path.startswith("/admin"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            f = open(curdir + sep + "/includes/admin_panel.html")
            self.wfile.write(f.read().encode("utf-8"))
            f.close()
            f = open(data_path + "/active_passive_list.json", 'r')
            list_of_files = json.load(f)

            for file in list_of_files:
                if list_of_files[file]:
                    var = '<p style="color:green">' + file + ' status: Active</p>'
                    deactivate = '<form style="border: 1px solid black; padding: 5px;" action="/command">' + var + ' <input type="hidden" name="execute" value="deactivate+' + file + '"/>' + '<input type="submit" value="Deactivate" />' + '</form>'

                    self.wfile.write(deactivate.encode("utf-8"))
                else:
                    var = '<p style="color:red">' + file + " status: Not Active</p>"
                    deactivate = '<form style="border: 1px solid black; padding: 5px;" action="/command">' + var + ' <input type="hidden" name="execute" value="activate+' + file + '"/>' + '<input disabled type="submit" value="Deactivate" />' + '<input type="submit" value="Activate" />' + '</form>'

                    self.wfile.write(deactivate.encode("utf-8"))
            return

        # commands
        if self.path.startswith("/command"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            f = open(curdir + sep + "/includes/admin_panel.html")
            # self.wfile.write(f.read().encode("utf-8"))
            command = self.path[17:]
            if command == 'forceindex':
                do_index()
                self.wfile.write('<p>Force index done</p>'.encode("utf-8"))

            if command.startswith('deactivate'):
                command = command[13:]
                command = command.replace("+", " ")
                acive_passive_files.ActivePassive.deactivate_file(command)

                self.wfile.write('<p>Force index done</p>'.encode("utf-8"))
                self.wfile.write('<p>Deactivated file</p>'.encode("utf-8"))

            if command.startswith('activate'):
                command = command[11:]
                command = command.replace("+", " ")
                acive_passive_files.ActivePassive.activate_file(command)

            back = '<form style="float: right; margin: 10px" action="/admin">' + '<input style="margin: 10px" type="submit" value="Back to Admin panel" />' + '</form>'
            self.wfile.write(back.encode("utf-8"))
            return

        if self.path.startswith("/send"):
            # self.path = "/includes/index.html"

            search_params = self.path

            # self.path = "/includes/index.html"

            search_params = search_params.replace("%28", "(")
            search_params = search_params.replace("%29", ")")
            search_params = search_params[13:]
            search_params = search_params.split("+")
            query = ""
            for val in search_params:
                if val != '':
                    query = query + val + " "
            query = query[:-1]

            # response implementation
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('query', query)
            self.end_headers()

            query_results, query_time = search.search(query)
            # NO results found
            if not query_results:
                # render page template
                f = open(curdir + sep + "/includes/index.html")
                self.wfile.write(f.read().encode("utf-8"))

                # render data
                to_wright = '<h1 ="">No Results for searched "' + query + '"</h1>'
                self.wfile.write(to_wright.encode("utf-8"))
                return

            # results found

            # render page template
            f = open(curdir + sep + "/includes/index.html")
            self.wfile.write(f.read().encode("utf-8"))

            var = '<p>Search time: ' + str(query_time)
            self.wfile.write(var.encode("utf-8"))
            first_line = ""
            second_line = ""

            for file_name in query_results:  # try to correct indexed values
                # file_name = file_name[:-4]
                # file_name = file_name + ".txt"
                try:
                    arr = []
                    print(docs_path + file_name)
                    decoded_string = ""
                    with open(docs_path + "/" + file_name, 'rb') as f:
                        contents = f.read()
                        decoded_string = contents.decode("utf-8", "replace")

                    # for_preview = open(docs_path + "/" + file_name, 'rb')
                    while arr.__len__() < 20:
                        # contents = f.read()
                        # decoded_string = contents.decode("utf-8", "replace")
                        # line = for_preview.readline()
                        arr += self.cleaning2(decoded_string).split(" ")
                    count = 0
                    first_line = ""
                    second_line = ""
                    for word in arr:
                        if count <= 9:
                            first_line += word + " "
                        if 9 < count < 18:
                            second_line += word + " "
                        count += 1

                    first_line = '<div class="st">' + first_line + "\n" + second_line + '</div>' + '</div>'
                    f.close()
                except IOError:
                    print("Open file error")

                var = '"' + file_name + '"'
                to_wright = '<div class ="rendered_links_and_text">' + '<a class="rendered_links" target="_blank" href=' + var + ">" + file_name[
                                                                                                                       :-4] + "</a>"
                self.wfile.write(to_wright.encode("utf-8"))
                self.wfile.write(first_line.encode("utf-8"))
                # self.wfile.write(second_line.encode("wtf-8"))

            f.close()
            return

        if self.path == "/":
            self.path = "/includes/index.html"
            pass

        try:
            # print(self.path)
            # Check the file extension required and
            # set the right mime type

            sendReply = False
            finalFile = False
            icon = False
            if self.path.endswith(".txt"):
                mimetype = 'text/html'
                # self.path = "/docs" + self.path
                sendReply = True
                finalFile = True

            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                self.path = "/includes" + self.path
                sendReply = True
            if self.path.endswith(".ico"):
                mimetype = 'image/x-icon'
                self.path = "/includes" + self.path
                icon = True
                sendReply = True

            if sendReply:
            #     if finalFile:
            #         f = open(curdir + sep + self.path)
            #         for line in f:
            #             for word in line:
            #                 if word == self.search_array[0]:
            #                     to_post_to_file = '<b>' + self.search_array[0] + '</b>'
            #                     self.wfile.write(to_post_to_file.encode("utf-8"))
            #                 else:
            #                     self.wfile.write(word.encode("utf-8"))


            #     self.wfile.write('<a style={padding: 100px;} href="/">Back to main page</a>'.encode("utf-8"))
            #
            # Open the static file requested and send it
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()

                if icon:
                    f = open(curdir + sep + self.path, 'rb')
                    self.wfile.write(f.read())
                    return
                elif finalFile:
                    file_path = self.path
                    file_path = file_path.replace("%20", " ")
                    f = open(docs_path + sep + file_path, 'rb')
                    # print to page text
                    decoded_string = ""
                    with open(docs_path + "/" + file_path, 'rb') as f:
                        contents = f.read()
                        decoded_string = contents.decode("utf-8", "replace")

                    cleaned_string = ""
                    for char in decoded_string:
                        if self.is_ascii(char):
                            cleaned_string = cleaned_string + char
                    var = self.headers
                    query = ""
                    for val in var:
                        if val == "Referer":
                            query = var[val]

                    query = query[34:]
                    search_params = query.replace("%28", "(")
                    search_params = search_params.replace("%29", ")")
                    search_params = search_params.split("+")
                    query = ""
                    for val in search_params:
                        if val != '':
                            query = query + val + " "
                    query = query[:-1]

                    query = query.replace("(", "")
                    query = query.replace(")",  "")

                    query = query.split(" ")

                    set_query = set(query)
                    query_literals = set_query - {"AND", "OR", "NOT", ")", "(", ""}
                    words = cleaned_string.split(" ")

                    # file name
                    file_path = file_path[1:]
                    var = '<h3>' + file_path[:-4] + '</h3>'
                    self.wfile.write(var.encode("utf-8"))
                    cleaned_query_literals = {''}
                    cleaned_query_literals.pop()
                    for word in query_literals:
                        word = self.cleaning2(word)
                        cleaned_query_literals.add(word)

                    # file text
                    for word in words:
                        if self.cleaning2(word) in cleaned_query_literals:
                            big_word = '<b><u>' + word + '</u></b>' + " "
                            self.wfile.write(big_word.encode("utf-8"))
                        else:
                            word = word + " "
                            self.wfile.write(word.encode("utf-8"))


                    # self.wfile.write(cleaned_string.encode("utf-8"))
                    self.wfile.write('<p><a style={padding: 100px;} href="/">Back to main page</a></p>'.encode("utf-8"))
                    f.close()
                else:
                    f = open(curdir + sep + self.path)
                    self.wfile.write(f.read().encode("utf-8"))
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer((hostName, hostPort), myHandler)

    do_index()


    # run_spider()                                              #spider and indexer
    # index_file()
    # Wait forever for incoming http requests
    print('Started http server on port ', hostPort)
    server.serve_forever()


except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()


