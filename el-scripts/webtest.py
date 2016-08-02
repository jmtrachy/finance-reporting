__author__ = 'jamest'

import argparse
import base64
import http.client
import os

_method_GET = "GET"
_method_POST = "POST"

_header_consumer_key = "X-ConsumerKey"
_header_content_type = "Content-Type"
_header_accept = "Accept"
_header_authorization = "Authorization"

_accept_XML = "application/xml"
_accept_JSON = "application/json"


class HttpRequest():
    def __init__(self):
        self.method = ""
        self.host = ""
        self.url = ""
        self.protocol = "HTTP/1.1"
        self.headers = dict()
        self.ssl = False
        self.body = None


class WebService():
    @staticmethod
    def send_request(http_req):

        if http_req.ssl:
            conn = http.client.HTTPSConnection(http_req.host)
        else:
            conn = http.client.HTTPConnection(http_req.host)

        if http_req.method == "POST":
            http_req.headers["Content-Length"] = len(http_req.body)

        # Added just to make sure we don't run into any limitations
        http_req.headers["X-RateLimitBypass"] = "TRUE"

        conn.request(http_req.method, http_req.url, http_req.body, http_req.headers)
        response_data = conn.getresponse().read().decode("utf-8")
        conn.close()
        return response_data


class RequestFactory():

    # Reads a properly formatted file and creates an HttpRequest object.  Format is:
    # Line 1 = "method protocol://domain/url protocolVersion"
    # Line 1 example "GET http://www.concur.com/fileService HTTP/1.1"
    # Line 2 - n = HTTP Headers
    # Line n + 1 = blank line to separate headers from body
    # Line n + 2 - x = body for post / put requests
    @staticmethod
    def read_request_from_file(file_name, host, port):
        f = open(file_name, "r")

        request_from_file = HttpRequest()

        if f is not None:
            counter = 1
            headers_complete = False

            for line in f:
                if line.endswith("\n"):
                    line = line[:-1]
                if counter == 1:
                    RequestFactory.parse_base_info(request_from_file, line, host, port)
                elif headers_complete is False:
                    if line == "":
                        headers_complete = True
                    else:
                        RequestFactory.parse_header(request_from_file, line)
                else:
                    if request_from_file.body is not None:
                        request_from_file.body = request_from_file.body + "\n" + line
                    else:
                        request_from_file.body = line
                counter += 1

        return request_from_file

    @staticmethod
    def parse_base_info(request_from_file, request_info, host, port):
        request_info = request_info.replace("{{HOST}}", host)
        request_info = request_info.replace("{{PORT}}", port)
        base_info = request_info.split(" ")
        request_from_file.method = base_info[0]
        request_from_file.protocol = base_info[2]

        if request_from_file.protocol.find("\n") != -1:
            request_from_file.protocol = request_from_file.protocol[:-1]

        full_url = base_info[1]
        colon_position = full_url.find(":")
        if colon_position == 4:
            request_from_file.ssl = False
        else:
            request_from_file.ssl = True

        domain_plus_url = full_url[colon_position + 3:]
        end_domain_position = domain_plus_url.find("/")

        request_from_file.host = domain_plus_url[:end_domain_position]
        request_from_file.url = domain_plus_url[end_domain_position:]

    @staticmethod
    def parse_header(request_from_file, header_line):
        colon_position = header_line.find(":")

        header_key = header_line[:colon_position]
        header_value = header_line[colon_position + 2:]

        if header_key == _header_authorization:
            header_value = RequestFactory.parse_auth_header(header_value)

        request_from_file.headers[header_key] = header_value

    # Returns the header value - different for various authentication methods
    @staticmethod
    def parse_auth_header(header_value):
        auth_tokens = header_value.split(" ")
        auth_header_value = None

        if auth_tokens[0] == "Basic":
            auth_header_value = auth_tokens[0] + " " + base64.b64encode(auth_tokens[1].encode("utf-8")).decode("utf-8")
        else:
            auth_header_value = header_value

        return auth_header_value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gathering arguments')
    parser.add_argument("-f", required=True, dest="file_name", action="store",
                        help="The first file containing a request to perform")
    parser.add_argument("-f2", required=False, dest="file_name_2", action="store",
                        help="The second call to perform")
    parser.add_argument("-H", required=False, dest="host", action="store", help="Host of the request, defaults to looking for an environment variable of ELK_HOST")
    parser.add_argument("-p", required=False, dest="port", action="store", help="Port of the request, defaults to looking for an environment variable of ELK_PORT")
    args = parser.parse_args()

    host = os.environ.get("ELK_HOST")
    if args.host is not None:
        host = args.host

    port = os.environ.get("ELK_PORT")
    if args.port is not None:
        port = args.port

    req1 = RequestFactory.read_request_from_file(args.file_name, host, port)
    print(WebService.send_request(req1))

    if args.file_name_2 is not None:
        req2 = RequestFactory.read_request_from_file(args.file_name_2)
        print(WebService.send_request(req2))