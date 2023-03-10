import pandas as pd

class Execution:
    def __init__(self, data):
        self.data = data
    
    def __eq__(self, other):
        if type(other) == str:
            return self.data['id'] == other
        return self.data['id'] == other.data['id']

class Trade:
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        if type(other) == str:
            return self.data['id'] == other
        return self.data['id'] == other.data['id']

    def __contains__(self, other):
        if isinstance(other, Execution):
            return other.data['tid'] == self.data['id']
        return False
    
class Executions:
    def __init__(self, user):
        self.user = user

    def load(self):
        pass
    
    def get_by_tid(self, tid):
        pass

    def get_by_id(self, id):
        pass

    def get_all(self):
        pass

    def create(self, tid, data):
        pass
    
    def update(self, id, data):
        pass

    def delete(self, id):
        pass

    def delete_all(self, tid):
        pass

class Trades:
    def __init__(self, user):
        self.user = user

    def load(self):
        pass

    def get_by_id(self, id):
        pass

    def get_all(self):
        pass

    def create(self, data):
        pass

    def update(self, id, data):
        pass

    def delete(self, id):
        pass

    def delete_all(self):
        pass