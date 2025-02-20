import json
class Airport():
    def __init__(self,airport_file):
        self.nodes = []
    def load_airport_data(self,airport_file):
        with open(airport_file,"r") as fs:
            data = json.load(fs)
            