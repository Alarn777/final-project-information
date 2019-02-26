import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import cgi
from json import JSONDecodeError
from os import curdir, sep
import os

from indexer import cleaning2, index_file
from query_logic import process_query
from spider import run_spider

hostName = "localhost"
hostPort = 9000

PORT_NUMBER = 8080


class myHandler(BaseHTTPRequestHandler):

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
        if self.path.startswith("/send"):
            # self.path = "/includes/index.html"

            search_params = self.path
            search_params = search_params[13:]
            search_array = search_params.split("+")
            process_query(search_params, self)

            # if search_array.__len__() > 0:
            #     have_parameters = True
            json_path = "/indexes/"

            max_occurences_in_file = {}
            for filename in os.listdir(curdir + json_path):
                if filename.startswith("."):
                    continue
                try:

                    f = open(curdir + json_path + filename, 'r')
                    try:
                        datastore = json.load(f)
                        if "words" in datastore:
                            if search_array[0] in datastore["words"]:
                                max_occurences_in_file[datastore["name"]] = int(datastore["words"][search_array[0]])

                    except JSONDecodeError:
                        pass

                except IOError:
                    print("Faulty file detected!" + filename)
                    pass

            max_file_name = ""
            max_value = 0

            for filenames in max_occurences_in_file:
                if int(max_occurences_in_file[filenames]) > max_value:
                    max_value = int(max_occurences_in_file[filenames])
                    max_file_name = filenames

            max_file_name = max_file_name[:-4]
            max_file_name = max_file_name + ".txt"
            # f = open(curdir + sep + "/files/" + max_file_name)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            f = open(curdir + sep + "/includes/index.html")
            self.wfile.write(f.read().encode("utf-8"))

            first_line = ""
            second_line = ""

            for filenames in sorted(max_occurences_in_file, key=max_occurences_in_file.get,
                                    reverse=True):  # try to correct indexed values
                # pass

                # for filenames in max_occurences_in_file:
                file_name = filenames
                file_name = file_name[:-4]
                file_name = file_name + ".txt"
                try:
                    arr = []
                    for_preview = open(curdir + "/files/" + file_name)
                    while arr.__len__() < 20:
                        line = for_preview.readline()
                        arr += cleaning2(line).split(" ")
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
                    for_preview.close()
                except IOError:
                    print("Open file error")

                var = '"' + file_name + '"'
                to_wright = '<div class ="rendered_links_and_text">' + '<a class="rendered_links" href=' + var + ">" + file_name[
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
                self.path = "/files/" + self.path
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

                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                # bla = f.readline()
                if icon:
                    f = open(curdir + sep + self.path, 'rb')
                    self.wfile.write(f.read())
                    return

                self.wfile.write(f.read().encode("utf-8"))
                if finalFile:
                    self.wfile.write('<a style={padding: 100px;} href="/">Back to main page</a>'.encode("utf-8"))
                f.close()

            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer((hostName, hostPort), myHandler)




    # run_spider()                                              #spider and indexer
    # index_file()
    # Wait forever for incoming http requests
    print('Started http server on port ', hostPort)
    server.serve_forever()


except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
