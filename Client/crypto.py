import base64


def write_b64(name, data):
    try:
        file_content = base64.b64decode(data)
        with open(name, "wb+") as f:
            f.write(file_content)
    except Exception as e:
        print(str(e))


def read_b64(name):
    with open(name, "rb") as f:
        file_content = f.read()
        return base64.b64encode(file_content).decode("utf-8")
