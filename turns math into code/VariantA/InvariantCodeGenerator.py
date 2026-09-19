import math

class InvariantCodeGenerator:
    def __init__(self, graph):
        self.graph = graph

    def _build_scope(self, engine):
        return {
            "__builtins__": __builtins__,
            "engine": engine,
            "math": math,
        }

    def generate_operator_functions(self):
        funcs = []

        for name, spec in self.graph.get("operators", {}).items():
            formula = spec.get("formula")
            cond_if = spec.get("if")
            cond_do = spec.get("do")

            def make_func(formula=formula, cond_if=cond_if, cond_do=cond_do):
                def fn(engine):
                    scope = self._build_scope(engine)
                    if cond_if:
                        if eval(cond_if, scope, scope):
                            if cond_do:
                                exec(cond_do, scope, scope)
                    if formula:
                        exec(formula, scope, scope)
                return fn

            funcs.append(make_func())

        return funcs

    def generate_invariant_functions(self):
        funcs = {}

        for name, spec in self.graph.get("invariants", {}).items():
            formula = spec.get("formula")

            def make_inv(formula=formula):
                def fn(engine):
                    scope = self._build_scope(engine)
                    return eval(formula, scope, scope)
                return fn

            funcs[name] = make_inv()

        return funcs

    def generate_watcher_functions(self):
        funcs = []

        for name, spec in self.graph.get("watchers", {}).items():
            trigger = spec.get("trigger")
            action = spec.get("action")

            def make_watch(trigger=trigger, action=action):
                def fn(engine):
                    scope = self._build_scope(engine)
                    if eval(trigger, scope, scope):
                        exec(action, scope, scope)
                return fn

            funcs.append(make_watch())

        return funcs

    def generate_collapse_functions(self):
        funcs = []

        for name, spec in self.graph.get("collapse_rules", {}).items():
            trigger = spec.get("trigger")
            action = spec.get("action")

            def make_collapse(trigger=trigger, action=action):
                def fn(engine):
                    scope = self._build_scope(engine)
                    if eval(trigger, scope, scope):
                        exec(action, scope, scope)
                return fn

            funcs.append(make_collapse())

        return funcs
