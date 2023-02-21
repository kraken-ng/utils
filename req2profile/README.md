# Req2profile

This utility allows you to transform a Burpsuite request to a **Connection Profile** (JSON) compatible with Kraken.

## Usage

```
usage: req2profile.py [-h] --request-file REQUEST_FILE --url URL --password PASSWORD --request-data-type
                      {HEADER,COOKIE,FIELD} --request-data-key REQUEST_DATA_KEY --request-password-type
                      {HEADER,COOKIE,FIELD} --request-password-key REQUEST_PASSWORD_KEY --response-data-type
                      {HEADER,COOKIE,FIELD} --response-data-key RESPONSE_DATA_KEY [--skip-ssl] -o OUTPUT

Script to convert a Burpsuite request into Kraken profile (coded by @secu_x11)

optional arguments:
  -h, --help            show this help message and exit
  --request-file REQUEST_FILE
                        Request File to parse
  --url URL             Complete URL where the agent is located
  --password PASSWORD   Password used in for autentication and encryption
  --request-data-type {HEADER,COOKIE,FIELD}
                        Type of HTTP field to encapsulate the request data
  --request-data-key REQUEST_DATA_KEY
                        Name of the field to contain the request data
  --request-password-type {HEADER,COOKIE,FIELD}
                        Type of HTTP field to encapsulate the password
  --request-password-key REQUEST_PASSWORD_KEY
                        Name of the field to contain the password
  --response-data-type {HEADER,COOKIE,FIELD}
                        Type of HTTP field to encapsulate the response data
  --response-data-key RESPONSE_DATA_KEY
                        Name of the field to contain the response data
  --skip-ssl            Ignore verifying the SSL certificate in requests (for self-signed certificates)
  -o OUTPUT, --output OUTPUT
                        Output JSON filepath of the connection profile

```

## Examples

Here are some examples of use:

```bash
python req2profile.py \
    --request-file ./examples/get_request.burp \
    --url 'http://localhost:8000/agent.php' --password 'P4ssw0rd!' \
    --request-data-type 'FIELD' --request-data-key 'data' \
    --request-password-type 'HEADER' --request-password-key 'X-Authorization' \
    --response-data-type 'FIELD' --response-data-key 'data' \
    --output custom_profile_get.json

python req2profile.py \
    --request-file ./examples/post_request.burp \
    --url 'http://localhost:8000/agent.php' --password 'P4ssw0rd!' \
    --request-data-type 'FIELD' --request-data-key 'data' \
    --request-password-type 'HEADER' --request-password-key 'X-Authorization' \
    --response-data-type 'FIELD' --response-data-key 'data' \
    --output custom_profile_post.json

python req2profile.py \
    --request-file ./examples/get_request.burp \
    --url 'https://localhost:8000/agent.php' --password 'P4ssw0rd!' \
    --request-data-type 'FIELD' --request-data-key 'data' \
    --request-password-type 'HEADER' --request-password-key 'X-Authorization' \
    --response-data-type 'FIELD' --response-data-key 'data' \
    --output custom_profile_get.json \
    --skip-ssl
```

Additionally, an [examples](examples) directory is provided with examples of existing Burpsuite requests and Connection Profiles.
