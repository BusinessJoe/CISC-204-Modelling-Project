import sys
from pprint import pprint
from src.file_reader import read_file

sys.setrecursionlimit(10 ** 6)


def summarize(solution):
    """Summarizes the solution by printing out certain propositions"""
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
    # Read model from file
    with open(sys.argv[1], encoding="utf8") as f:
        encoding = read_file(f, True)

    satisfiable = encoding.is_satisfiable()
    print(f"Satisfiable: {satisfiable}\n")

    if satisfiable:
        num_solutions = encoding.count_solutions()
        if num_solutions == 1:
            print("There is 1 solution.\n")
        else:
            print(f"There are {num_solutions} solutions.\n")
        print("One solution is:")
        s = encoding.solve()

        summarize(s)
