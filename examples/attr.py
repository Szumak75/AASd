from jsktoolbox.attribtool import NoDynamicAttributes


class Keys(NoDynamicAttributes):
    """Keys definition class.

    For internal purpose only.
    """

    BUFFERED = "__buffered__"


example = {}
example[Keys.BUFFERED] = True

print(example)

# Nie można zmienić wartości właściwości

try:
    Keys.BUFFERED = 1
except AttributeError as e:
    print(e)

print(Keys.BUFFERED)
