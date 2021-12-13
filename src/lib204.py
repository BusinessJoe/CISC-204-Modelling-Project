from nnf import And, dsharp, NNF, config


class Encoding(object):
    def __init__(self):
        self.constraints = []

    def vars(self):
        ret = set()
        for c in self.constraints:
            ret |= c.vars()
        return ret

    def size(self):
        ret = 0
        for c in self.constraints:
            ret += c.size()
        return ret

    def valid(self):
        return And(self.constraints).valid()

    def negate(self):
        return And(self.constraints).negate()

    def add_constraint(self, c):
        assert isinstance(c, NNF), "Constraints need to be of type NNF"
        self.constraints.append(c)

    @config(sat_backend="pysat")
    def is_satisfiable(self):
        return And(self.constraints).simplify().satisfiable()

    @config(sat_backend="pysat")
    def solve(self):
        return And(self.constraints).simplify().solve()

    def count_solutions(self, lits=[]):
        if lits:
            T = And(self.constraints + lits)
        else:
            T = And(self.constraints)
        T = T.simplify()
        if not T.satisfiable():
            return 0

        return dsharp.compile(
            T.to_CNF(), executable="bin/dsharp", smooth=True
        ).model_count()

    def models(self):
        T = And(self.constraints)
        return dsharp.compile(T.to_CNF(), executable="bin/dsharp", smooth=True).models()

    def likelihood(self, lit):
        return self.count_solutions([lit]) / self.count_solutions()
