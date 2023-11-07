class ReadOnlyClass(type):
    def __setattr__(self, name, value):
        raise ValueError(name)


class Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    BUFFERED = "__buffered__"


example = {}
example[Keys.BUFFERED] = True

print(example)

# Nie można zmienić wartości właściwości

Keys.BUFFERED = 1
print(Keys.BUFFERED)

a = Keys()
print(a.BUFFERED)
a.BUFFERED = 7
