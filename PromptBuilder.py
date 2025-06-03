class PromptBuilder():
    def __init__(self):
        self.premise: list[str] = []
        self.end: list[str] = []
        self.data: list[str] = []
        self.data_only = False

    def add_data(self, data):
        self.data.append(data)
        return self

    def add_end(self, end):
        self.end.append(end)
        return self

    def set_data_only(self, data_only):
        self.data_only = data_only
        return self

    def add_premise(self, premise):
        self.premise.append(premise)
        return self

    def build(self):
        if len(self.data) == 0:
            print("This prompt did not contain any data, was it intentional ?")
        data = " ".join(self.data)
        if self.data_only:
            return data
        else :
            end = "".join(self.end)
            premise = "".join(self.premise)
            return f"{premise}\n{data}\n{end}"
