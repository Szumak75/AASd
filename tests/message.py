#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 07.12.2023

Purpose:
"""


class Test(object):
    """"""

    def __init__(self):
        """Constructor."""

    def __setattr__(self, name, value):
        """"""
        print(self.__dict__)
        print(f"ATTR->name: {name}")
        print(f"ATTR->value: {value}")

    def message(self, text: str) -> None:
        """"""
        print(text)

    @property
    def message_info(self) -> None:
        """"""
        return

    @message_info.setter
    def message_info(self, value: str) -> None:
        """"""
        self.message(text=value)

    # @property
    # def message(self) -> None:
    # return

    # @message.setter
    # def message(self, value: str) -> None:
    # raise AttributeError(
    # "Cannot assign to 'message' attribute. Use 'message_info' instead."
    # )

    # @message.deleter
    # def message(self) -> None:
    # del self._message


"""
Dekorator @message.deleter w Pythonie jest używany do zdefiniowania zachowania,
które ma zostać wykonane, gdy atrybut oznaczony jako property jest usuwany
(czyli gdy używamy operatora del na tym atrybucie). W przypadku poprzedniego
przykładu, dekorator @message.deleter jest zaimplementowany, ale jego funkcja
nie wykonuje żadnych konkretnych działań. Niemniej jednak, możesz zdefiniować
swoje własne zachowanie, które zostanie wykonane, gdy właściwość message jest usuwana.
"""

if __name__ == "__main__":
    test = Test()
    test.message_info = "to jest test"
    test.message = "xxx"
    test.message_info = "to jest test nr 2"


# #[EOF]#######################################################################
