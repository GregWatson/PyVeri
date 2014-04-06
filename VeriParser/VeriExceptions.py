# Simulator exception types

import exceptions

class RuntimeInfiniteLoopError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

class TestAssertionError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

class InsufficientWidthError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args
