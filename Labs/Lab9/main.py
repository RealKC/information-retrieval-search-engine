def pagerank(pages: list[int], topology: list[list[int]]) -> list[float]:
    q = 0.15

    old_PR = []
    PR = []
    E = []

    def no_more_variations():
        epsilon = 10e-10
        if len(old_PR) == 0:
            return False

        for i in range(len(PR)):
            if PR[i] - old_PR[i] > epsilon:
                return False

        return True

    for p in pages:
        PR.append(q / len(pages))
        E.append(1 / len(pages))

    while not no_more_variations():
        new_PR = []

        for p in pages:
            pr_over_nw = 0

            for w in pages:
                if topology[w][p] == 0:
                    continue

                nw = sum(topology[w])

                if nw == 0:
                    continue

                pr_over_nw += PR[w] / nw

            new_PR.append(((1 - q) * pr_over_nw) + E[p])

        old_PR = PR.copy()

        c = 1 / sum(new_PR)

        for p in pages:
            PR[p] = c * new_PR[p]

    return PR


PAGES = list(range(0, 11))
TOPOLOGY = [
    # 1  2  3  4  5  6  7  8  9  10 11
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
]


def main():
    ranks = pagerank(PAGES, TOPOLOGY)

    sorted_ranks = sorted(
        [(idx + 1, val) for idx, val in enumerate(ranks)],
        key=lambda v: v[1],
        reverse=True,
    )

    for idx, val in sorted_ranks:
        print(f"{idx}: {val}")

    print(f"ranks sum: {sum(ranks)}")


if __name__ == "__main__":
    main()
