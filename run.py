from nnf import Var
from src.file_reader import read_file
from src.lib204 import Encoding

import sys

sys.setrecursionlimit(10 ** 6)


def summarize(solution):
    # Do some filtering
    solution = {k: v for k, v in solution.items() if isinstance(k, str)}

    alien_coords = {
        k.split(":")[1] for k, v in solution.items() if v and k.split(":")[0] == "alien"
    }
    house_coords = {
        k.split(":")[1] for k, v in solution.items() if v and k.split(":")[0] == "house"
    }
    rail_coords = {
        k.split(":")[1] for k, v in solution.items() if v and k.split(":")[0] == "rail"
    }

    pprint({k: v for k, v in solution.items() if v and k.split(":")[0] == "alien"})
    pprint({k: v for k, v in solution.items() if v and k.split(":")[0] == "house"})
    pprint(
        {k: v for k, v in solution.items() if v and k.split(":")[0].startswith("rail")}
    )
    pprint(
        {
            k: v
            for k, v in solution.items()
            if k.split(":")[1] in alien_coords and k.startswith("alien_sat")
        }
    )
    pprint(
        {
            k: v
            for k, v in solution.items()
            if k.split(":")[1] in house_coords and k.startswith("house_sat")
        }
    )
    pprint(
        {
            k: v
            for k, v in solution.items()
            if k.split(":")[1] in rail_coords and k.startswith("train_")
        }
    )


if __name__ == "__main__":
    from pprint import pprint

    with open("data/xml/example_full_empty.xml", encoding="utf8") as f:
        T = read_file(f, True)

    satisfiable = T.is_satisfiable()
    print("\nSatisfiable: %s" % satisfiable)

    if satisfiable:
        print(T.size())
        print(f"# Solutions: {T.count_solutions()}")
        print("Solutions:")
        models = list(T.models())

        for m in models:
            summarize(m)
