class FileNotFoundOnServerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class FilenameNotSetError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DataFrameNotCreatedError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidDateError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
