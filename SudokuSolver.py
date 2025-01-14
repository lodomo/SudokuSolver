import sys

import numpy as np


class List(list):
    pass


class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        """Do not return anything, modify board in-place instead."""
        solver = SudokuSolver(board)
        solved = solver.solve()
        self.updateBoardFromGrid(board, solved)
        return None

    def updateBoardFromGrid(self, board, grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    board[i][j] = str(grid[i][j])


class Cell:
    default_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}

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

    def updateCandidates(self, anti_set):
        if self.value:
            return

        self.candidates -= anti_set


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
            cell.updateCandidates(self.values)


class SudokuSolver:
    def __init__(self, board: list):
        self.board = [[Cell(i, j) for j in range(9)] for i in range(9)]

        self.rows = [Cluster() for _ in range(9)]
        self.cols = [Cluster() for _ in range(9)]
        self.boxs = [Cluster() for _ in range(9)]

        for row in range(9):
            for col in range(9):
                if board[row][col] != ".":
                    self.board[row][col].value = int(board[row][col])

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
            changed += self.nakedSingles()
            changed += self.hiddenSingles()
        return self.board

    def setCell(self, val, cell):
        cell.setVal(val)
        self.rows[cell.row].updateCandidates()
        self.cols[cell.col].updateCandidates()
        self.boxs[cell.box].updateCandidates()

    def nakedSingles(self):
        changed = 0
        for row in self.rows:
            for cell in row.cells:
                if len(cell.candidates) == 1:
                    self.setCell(cell.candidates.pop(), cell)
                    changed += 1
        return changed

    def hiddenSingles(self):
        changed = 0
        for row in self.rows:
            changed += self.hiddenSingle(row)
        for col in self.cols:
            changed += self.hiddenSingle(col)
        for box in self.boxs:
            changed += self.hiddenSingle(box)
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


if __name__ == "__main__":
    board = sys.stdin.read()
    board = [list(row.strip()) for row in board.split("\n")]
    if board[-1] == []:
        board.pop()
    solver = SudokuSolver(board)
    solver.solve()
    solver.printCandidates()

"""
class SudokuSolver:
    total_cells = 81
    default_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def __init__(self, board: list):
        self.rows = [set() for _ in range(9)]
        self.cols = [set() for _ in range(9)]
        self.boxs = [set() for _ in range(9)]
        self.cans = [[set() for _ in range(9)] for _ in range(9)]
        self.mt_cells = 81
        self.board = self.list_2D_to_np_array(board)
        self.initializeCandidates()

    def list_2D_to_np_array(self, board):
        grid = np.zeros((9, 9), dtype=int)
        for i in range(9):
            for j in range(9):
                if board[i][j] != ".":
                    grid[i][j] = int(board[i][j])
        return grid

    def initializeCandidates(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    self.cans[row][col] = self.default_set
                else:
                    self.rows[row].add(self.board[row][col])
                    self.cols[col].add(self.board[row][col])
                    self.boxs[self.getBoxIndex(row, col)].add(
                        self.board[row][col])
                    self.mt_cells -= 1
        self.updateCandidatesFromSetValues()

    def updateCandidatesFromSetValues(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    self.cans[row][col] = (
                        self.default_set
                        - self.rows[row]
                        - self.cols[col]
                        - self.boxs[self.getBoxIndex(row, col)]
                    )

    def getBoxIndex(self, row, col):
        return (row // 3) * 3 + col // 3

    def printPretty(self, board):
        print("-------------------------")
        for i in range(9):
            p = ["|"]
            for j in range(9):
                if board[i][j] == "." or board[i][j] == 0:
                    p.append(" ")
                else:
                    p.append(board[i][j])
                if j % 3 == 2:
                    p.append("|")
            print(" ".join(map(str, p)))
            if i % 3 == 2:
                print("-------------------------")
        print(f"Empty Cells: {self.mt_cells}")
        print(f"Filled Cells: {self.total_cells - self.mt_cells}")

    def printCandidates(self):
        output = [[" " for _ in range(27)] for _ in range(27)]

        for row in range(9):
            for col in range(9):
                start_row, start_col = row * 3, col * 3

                if self.board[row][col] != 0:  # If the cell has a number
                    num = str(self.board[row][col])
                    output[start_row + 1][start_col + 1] = num
                else:  # If the cell is empty, print candidates
                    for candidate in self.cans[row][col]:
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

    def possibleCombinations(self):
        candidate_count = []
        for row in range(9):
            for col in range(9):
                candidate_count.append(len(self.cans[row][col]))

        product = 1
        for candidate in candidate_count:
            if candidate == 0:
                continue
            product *= candidate
        print(f"Candidate Count: {candidate_count}")
        print(f"Possible Combinations: {product}")
        return

    def solve(self):
        """ """
        changed = 1
        while changed:
            changed = 0
            changed += self.nakedSingles()
            changed += self.hiddenSingles()
            changed += self.nakedDoubles()
            changed += self.hiddenDoubles()
            changed += self.halfDoubles()
            changed += self.nakedTriples()
            changed += self.hiddenTriples()
            changed += self.blocking()
        pass

    def nakedSingles(self):
        changed = 0
        for row in range(9):
            for col in range(9):
                if len(self.cans[row][col]) == 1:
                    val = self.cans[row][col].pop()
                    self.lockValue(val, row, col)
                    changed += 1
        return changed

    def hiddenSingles(self):
        changed = 0
        for row in range(9):
            for col in range(9):
                changed += self.hiddenSingleRow(row, col)
                changed += self.hiddenSingleCol(row, col)

        for box in range(9):
            changed += self.hiddenSingleBox(box)
        return changed

    def hiddenSingleRow(self, row_y, col_x):
        this_set = self.cans[row_y][col_x]
        dif_set = set()
        for col in range(9):
            if col == col_x:
                continue
            dif_set = dif_set.union(self.cans[row_y][col])

        candidate = this_set - dif_set
        if len(candidate) == 1:
            candidate = candidate.pop()
            self.lockValue(candidate, row_y, col_x)
            return 1
        return 0

    def hiddenSingleCol(self, row_y, col_x):
        this_set = self.cans[row_y][col_x]
        dif_set = set()
        for row in range(9):
            if row == row_y:
                continue
            dif_set = dif_set.union(self.cans[row][col_x])

        candidate = this_set - dif_set
        if len(candidate) == 1:
            candidate = candidate.pop()
            self.lockValue(candidate, row_y, col_x)
            return 1
        return 0

    def hiddenSingleBox(self, box):
        row0 = (box // 3) * 3
        col0 = (box % 3) * 3

        for row_y in range(3):
            for col_x in range(3):
                row = row0 + row_y
                col = col0 + col_x
                this_set = self.cans[row][col]
                dif_set = set()
                for row_a in range(3):
                    for col_b in range(3):
                        if row_a == row_y and col_b == col_x:
                            continue
                        dif_set = dif_set.union(
                            self.cans[row0 + row_a][col0 + col_b])

                candidate = this_set - dif_set
                if len(candidate) == 1:
                    candidate = candidate.pop()
                    self.lockValue(candidate, row, col)
                    return 1
        return 0

    def nakedDoubles(self):
        return 0

    def nakedDoubleRow(self, row_y, col_x):
        cans = self.cans[row_y][col_x]
        if len(cans) != 2:
            return 0

        for col in range(9):
            if col == col_x:
                continue
            if cans == self.cans[row_y][col]:
                for col_z in range(9):
                    if col_z == col_x or col_z == col:
                        continue
                    self.cans[row_y][col_z] -= cans
                return 1
        return 0

    def nakedDoubleCol(self, row_y, col_x):
        cans = self.cans[row_y][col_x]
        if len(cans) != 2:
            return 0

        for row in range(9):
            if row == row_y:
                continue
            if cans == self.cans[row][col_x]:
                for row_z in range(9):
                    if row_z == row_y or row_z == row:
                        continue
                    self.cans[row_z][col_x] -= cans
                return 1
        return 0

    def nakedDoubleBox(self, box):
        return 0

    def hiddenDoubles(self):
        return 0

    def halfDoubles(self):
        return 0

    def nakedTriples(self):
        return 0

    def hiddenTriples(self):
        return 0

    def blocking(self):
        return 0

    def lockValue(self, val, row, col):
        self.board[row][col] = val
        self.rows[row].add(val)
        self.cols[col].add(val)
        self.boxs[self.getBoxIndex(row, col)].add(val)
        self.mt_cells -= 1
        self.cans[row][col] = set()
        self.updateCandidatesFromSetValues()


if __name__ == "__main__":
    board = sys.stdin.read()
    board = [list(row.strip()) for row in board.split("\n")]
    if board[-1] == []:
        board.pop()
    for row in board:
        print(row)
    solver = SudokuSolver(board)
    solver.printPretty(solver.board)
    solver.printCandidates()
    solver.possibleCombinations()
    solver.solve()
    solver.printPretty(solver.board)
    solver.printCandidates()
    solver.possibleCombinations()


    def isSameBoard(self, board1, board2):
        for i in range(9):
            for j in range(9):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def solve(self):
        board_copy = None
        # print("Original")
        # self.printPretty(self.board)
        while (
            board_copy is None or not self.isSameBoard(self.board, board_copy)
        ) and self.empty_cells > 0:
            board_copy = np.copy(self.board)
            print("Solo Candidates")
            self.soloCandidate()
            self.updateCandidates()
            self.printPretty(self.board)

            print("Horizontal Scan")
            self.horizontalHiddenSingles()
            self.updateCandidates()
            self.printPretty(self.board)

            print("Vertical Scan")
            self.verticalHiddenSingles()
            self.printPretty(self.board)
            self.updateCandidates()

        print("Candidates")
        self.printCandidates()

        return self.board
"""
