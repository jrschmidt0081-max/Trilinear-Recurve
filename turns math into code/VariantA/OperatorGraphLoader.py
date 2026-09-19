import json

class OperatorGraphLoader:
    def __init__(self, path="operator_graph.json"):
        with open(path, "r") as f:
            self.graph = json.load(f)

    def get_operators(self):
        return self.graph.get("operators", {})

    def get_invariants(self):
        return self.graph.get("invariants", {})

    def get_watchers(self):
        return self.graph.get("watchers", {})

    def get_collapse_rules(self):
        return self.graph.get("collapse_rules", {})
