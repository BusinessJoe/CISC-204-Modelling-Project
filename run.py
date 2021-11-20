from nnf import Var
from src.file_reader import read_file
from src.lib204 import Encoding

import sys

sys.setrecursionlimit(10 ** 6)

if __name__ == "__main__":
    from pprint import pprint

    with open("data/xml/example_long.xml", encoding="utf8") as f:
        T, props = read_file(f)

    satisfiable = T.is_satisfiable()
    print("\nSatisfiable: %s" % satisfiable)

    if satisfiable:
        print(f"# Solutions: {T.count_solutions()}")
        print("Solution:")
        solution = T.solve()
        true_part = {k: v for k, v in solution.items() if v}
        false_part = {k: v for k, v in solution.items() if not v}
        pprint(true_part)
        pprint(false_part)

        print(T.likelihood(props["SA"][1, 1]))
