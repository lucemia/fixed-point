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


@recordable
async def async_add(a, b):
    return a + b


@recordable
async def async_multiply(a, b):
    return a * b


def outer(x):
    return add(x, 1) * 2
