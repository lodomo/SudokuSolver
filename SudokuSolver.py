import sys


class Cell:
    def __init__(self, row=-1, col=-1):
        self.row = row
        self.col = col
        self.box = (row // 3) * 3 + col // 3
        self.candidates = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        self.value = 0

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"{self.value}"

    def setVal(self, val):
        self.value = val
        self.candidates = set()

    def eliminateCandidates(self, anti_set):
        if self.value:
            return 0

        if self.candidates == anti_set:
            return 0

        temp = self.candidates.copy()

        self.candidates -= anti_set

        if self.candidates != temp:
            return 1
        return 0

    def guaranteeCandidates(self, pro_set):
        if self.value:
            return

        temp = self.candidates.copy()

        # & is the intersection operator
        self.candidates &= pro_set

        if self.candidates != temp:
            return 1
        return 0


class Cluster:
    def __init__(self):
        self.cells = []
        self.values = set()

    def __str__(self):
        string = []
        for cell in self.cells:
            string.append(str(cell))
        return " ".join(string)

    def __repr__(self):
        return self.__str__()

    def addCell(self, cell):
        self.cells.append(cell)
        if cell.value:
            self.values.add(cell.value)

    def updateCandidates(self):
        for cell in self.cells:
            if cell.value not in self.values:
                self.values.add(cell.value)

        for cell in self.cells:
            cell.eliminateCandidates(self.values)


class SudokuSolver:
    def __init__(self, board: list):
        self.board = [[Cell(i, j) for j in range(9)] for i in range(9)]

        self.rows = [Cluster() for _ in range(9)]
        self.cols = [Cluster() for _ in range(9)]
        self.boxs = [Cluster() for _ in range(9)]
        self.solved = 0

        for row in range(9):
            for col in range(9):
                if board[row][col] != "." and board[row][col] != 0:
                    self.board[row][col].setVal(int(board[row][col]))

                self.rows[row].addCell(self.board[row][col])
                self.cols[col].addCell(self.board[row][col])
                self.boxs[self.getBox(row, col)].addCell(self.board[row][col])

        for i in range(9):
            self.rows[i].updateCandidates()
            self.cols[i].updateCandidates()
            self.boxs[i].updateCandidates()

    def __str__(self):
        string = []
        for row in self.rows:
            string.append(str(row))
        return "\n".join(string)

    def boardToList(self):
        board = []
        for row in self.board:
            board.append([cell.value for cell in row])
        return board

    def getBox(self, row, col):
        return (row // 3) * 3 + col // 3

    def printCandidates(self):
        output = [[" " for _ in range(27)] for _ in range(27)]

        for row in range(9):
            for col in range(9):
                start_row, start_col = row * 3, col * 3

                if self.board[row][col].value != 0:  # If the cell has a number
                    num = str(self.board[row][col])
                    output[start_row + 1][start_col + 1] = num
                else:  # If the cell is empty, print candidates
                    for candidate in self.board[row][col].candidates:
                        # Map candidate numbers to positions in the 3x3 grid
                        candidate_row = (candidate - 1) // 3
                        candidate_col = (candidate - 1) % 3
                        output[start_row + candidate_row][start_col + candidate_col] = (
                            str(candidate)
                        )

        for i, line in enumerate(output):
            new_line = []
            for j in range(len(line)):
                if j % 3 == 0:
                    new_line.append("|")
                new_line.append(line[j])
            new_line.append("|")

            if i % 3 == 0:
                print("".join(["-" for _ in range(73)]))
            print(" ".join(new_line))
        print("".join(["-" for _ in range(73)]))

    def solve(self):
        changed = 1
        while changed:
            changed = 0
            if self.nakedSingles():
                print("Found naked singles")
                changed = 1
                continue

            if self.funcToAllClusters(self.hiddenSingle):
                print("Found hidden singles")
                changed = 1
                continue

            if self.funcToAllClusters(self.nakedDouble):
                print("Found naked doubles")
                changed = 1
                continue

            if self.funcToAllClusters(self.hiddenDouble):
                print("Found hidden doubles")
                changed = 1
                continue

        solved_cells = 0
        for row in self.board:
            for cell in row:
                if cell.value:
                    solved_cells += 1
        print(f"Solved {solved_cells} cells")
        if solved_cells == 81:
            return 1

        empty_candidate_cells = 0
        for row in self.board:
            for cell in row:
                if not cell.value and not cell.candidates:
                    empty_candidate_cells += 1
        if empty_candidate_cells:
            print(f"Empty candidate cells: {empty_candidate_cells}")
            return -1

        self.printCandidates()
        print("Time To DFS Guess")
        cell = self.firstUnsolvedCell()

        for candidate in self.board[cell[0]][cell[1]].candidates:
            print(f"Trying {candidate} at {cell}")
            board_copy = self.boardToList()
            board_copy[cell[0]][cell[1]] = candidate
            solver = SudokuSolver(board_copy)
            solver.printPretty()
            if solver.solve() == -1:
                print(f"Failed with {candidate} at {cell}")
                continue

            self.board = solver.board

        return 1

    def printPretty(self):
        for row in self.board:
            for cell in row:
                print(cell, end=" ")
            print()

    def firstUnsolvedCell(self):
        for row in range(9):
            for col in range(9):
                if not self.board[row][col].value:
                    return (row, col)

    def remainingCombinations(self):
        combos = 1
        for row in self.board:
            for cell in row:
                if not cell.value:
                    combos *= len(cell.candidates)
        return combos

    def setCell(self, val, cell):
        cell.setVal(val)
        self.solved += 1
        self.rows[cell.row].updateCandidates()
        self.cols[cell.col].updateCandidates()
        self.boxs[cell.box].updateCandidates()

    def funcToAllClusters(self, func):
        count = 0
        for row in self.rows:
            count += func(row)
        for col in self.cols:
            count += func(col)
        for box in self.boxs:
            count += func(box)
        return count

    def nakedSingles(self):
        changed = 0
        for row in self.rows:
            for cell in row.cells:
                if len(cell.candidates) == 1:
                    self.setCell(cell.candidates.pop(), cell)
                    changed += 1
        return changed

    def hiddenSingle(self, cluster):
        count = 0
        for cell in cluster.cells:
            if cell.value:
                continue

            this_set = cell.candidates
            dif_set = set()
            for other_cell in cluster.cells:
                if other_cell == cell:
                    continue
                dif_set = dif_set.union(other_cell.candidates)

            candidate = this_set - dif_set
            if len(candidate) == 1:
                self.setCell(candidate.pop(), cell)
                count += 1
        return count

    def nakedDouble(self, cluster):
        count = 0
        for i in range(9):
            if len(cluster.cells[i].candidates) == 2:
                for j in range(i + 1, 9):
                    if cluster.cells[i].candidates == cluster.cells[j].candidates:
                        for k in range(9):
                            if k == i or k == j:
                                continue
                            count += cluster.cells[k].eliminateCandidates(
                                cluster.cells[i].candidates
                            )
        return count

    def hiddenDouble(self, cluster):
        count = 0
        cand_map = {}
        for i in range(9):
            for candidate in cluster.cells[i].candidates:
                if candidate not in cand_map:
                    cand_map[candidate] = []
                cand_map[candidate].append(i)

        for key in list(cand_map.keys()):
            if len(cand_map[key]) != 2:
                cand_map.pop(key)

        for key in cand_map:
            for key2 in cand_map:
                if key == key2:
                    continue
                if cand_map[key] == cand_map[key2]:
                    for i in range(9):
                        if i not in cand_map[key]:
                            count += cluster.cells[i].eliminateCandidates(
                                {key, key2})
                        else:
                            count += cluster.cells[i].guaranteeCandidates(
                                {key, key2})

        return count


if __name__ == "__main__":
    board = sys.stdin.read()
    board = [list(row.strip()) for row in board.split("\n")]
    if board[-1] == []:
        board.pop()
    solver = SudokuSolver(board)
    solver.solve()
    solver.printCandidates()
    print("Remaining combinations:", solver.remainingCombinations())
