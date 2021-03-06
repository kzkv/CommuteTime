# -*- coding: UTF-8 -*-
import pprint


class _MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


_pprinter = _MyPrettyPrinter()


def pretty_print(obj):
    _pprinter.pprint(obj)
