class Station:
    def __init__(self, name):
        self.name = name
        self.info = dict()

    def set_info(self, index, line_name):
        self.info[line_name] = index