import argparse, json


def read_file_lines(filepath):
    with open(filepath, "r") as fd:
        return fd.read().splitlines()

def parse_request(url, request_lines, skip_ssl):
    http_method  = ""
    http_headers = {}
    http_cookies = {}
    http_fields  = {}
    http_skip_ssl = False

    # Parse HTTP Request Method
    fields = request_lines[0].split(" ")
    http_method = fields[0]
    
    # Parse HTTP Request Headers
    i = 1
    n = len(request_lines)
    while i < n:
        if request_lines[i] == "":
            i = i + 1
            break
        header_key, header_value = request_lines[i].split(": ")

        # Parse HTTP Request Cookies
        if header_key == "Cookie":
            fields = header_value.split(";")
            for field in fields:
                cookie_key, cookie_value = field.split("=")
                http_cookies[cookie_key] = cookie_value
        else:
            http_headers[header_key] = header_value
        i = i + 1
    
    if url.startswith("https://") and skip_ssl:
        http_skip_ssl = True

    # Parse HTTP Request Fields
    if http_method == "GET":
        if "?" not in url:
            return (http_method, http_headers, http_cookies, http_fields, http_skip_ssl)
        endpoint, params = url.split("?")
        fields = params.split("&")
        for field in fields:
            http_get_key, http_get_value = field.split("=")
            http_fields[http_get_key] = http_get_value
    elif http_method == "POST":
        if "&" not in request_lines[i]:
            return (http_method, http_headers, http_cookies, http_fields, http_skip_ssl)
        fields = request_lines[i].split("&")
        for field in fields:
            http_post_key, http_post_value = field.split("=")
            http_fields[http_post_key] = http_post_value

    return (http_method, http_headers, http_cookies, http_fields, http_skip_ssl)

def generate_profile(url, method, headers, cookies, fields, request_data_key, request_data_type, 
    password, request_password_key, request_password_type, response_data_key, response_data_type,
    skip_ssl):
    profile = {}
    profile["client"] = {
        "url" : url,
        "skip_ssl" : skip_ssl,
        "method" : method,
        "headers" : headers,
        "cookies" : cookies,
        "fields" : fields,
        "message" : {
            "secret" : {
                "type" : request_password_type,
                "key" : request_password_key,
                "value" : password
            },
            "data" : {
                "type" : request_data_type,
                "key" : request_data_key
            }
        }
    }
    profile["server"] = {
        "type" : response_data_type,
        "key" : response_data_key
    }
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to convert a Burpsuite request into Kraken profile (coded by @secu_x11)")
    parser.add_argument("--request-file", action='store', required=True, help="Request File to parse")
    parser.add_argument("--url", action='store', required=True, help="Complete URL where the agent is located")
    parser.add_argument("--password", action='store', required=True, help="Password used in for autentication and encryption")
    parser.add_argument("--request-data-type", action='store', choices=["HEADER","COOKIE","FIELD"], required=True, help="Type of HTTP field to encapsulate the request data")
    parser.add_argument("--request-data-key", action='store', required=True, help="Name of the field to contain the request data")
    parser.add_argument("--request-password-type", action='store', choices=["HEADER","COOKIE","FIELD"], required=True, help="Type of HTTP field to encapsulate the password")
    parser.add_argument("--request-password-key", action='store', required=True, help="Name of the field to contain the password")
    parser.add_argument("--response-data-type", action='store', choices=["HEADER","COOKIE","FIELD"], required=True, help="Type of HTTP field to encapsulate the response data")
    parser.add_argument("--response-data-key", action='store', required=True, help="Name of the field to contain the response data")
    parser.add_argument('--skip-ssl', action='store_true', help="Ignore verifying the SSL certificate in requests (for self-signed certificates)")
    parser.add_argument('-o', "--output", action='store', required=True, help="Output JSON filepath of the connection profile")
    args = parser.parse_args()

    request_lines = read_file_lines(args.request_file)
    http_method, http_headers, http_cookies, http_fields, skip_ssl = parse_request(args.url, request_lines, args.skip_ssl)
    profile = generate_profile(
        args.url,
        http_method,
        http_headers,
        http_cookies,
        http_fields,
        args.request_data_key,
        args.request_data_type,
        args.password,
        args.request_password_key,
        args.request_password_type,
        args.response_data_key,
        args.response_data_type,
        skip_ssl
    )
    with open(args.output, "w") as fd:
        json.dump(profile, fd)
    
    print(f"[+] Profile written to '{args.output}'")