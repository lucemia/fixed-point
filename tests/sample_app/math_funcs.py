from fixedpoint import recordable


@recordable
def add(a, b):
    return a + b


@recordable
def multiply(a, b):
    return a * b


@recordable
def get_config():
    return {"debug": True, "level": 3}


def outer(x):
    return add(x, 1) * 2
