from nnf import Var
from src.file_reader import read_file
from src.lib204 import Encoding


if __name__ == "__main__":
    from pprint import pprint

    with open("data/test1.ce") as f:
        T, props = read_file(f)

    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution:")
    solution = T.solve()
    pprint(solution)
