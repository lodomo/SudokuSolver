import sys


class Cell:
    def __init__(self, row: int = -1, col: int = -1, value: int = 0):
        self.row = row
        self.col = col
        self.box = (row // 3) * 3 + col // 3

        self.value = value
        self.candidates = {1, 2, 3, 4, 5, 6, 7, 8, 9}

        if value:
            self.candidates.clear()

    def __str__(self):
        if self.value:
            return f"{self.value}"
        return "~"

    def __repr__(self):
        return self.__str__()

    def set_val(self, val) -> None:
        """
        Sets the value of the cell to the given value.
        The candidates are cleared if the cell has is given a value.

        Raises a ValueError if the cell already has a value.
        """
        if self.value:
            raise ValueError(
                f"Cell {self.row}, {
                    self.col} already has a value"
            )

        self.value = val
        self.candidates.clear()
        return

    def remove_candidates(self, set_to_remove) -> int:
        """
        Removes all candidates in to_remove from the cell.

        If the cell has a value, it will not remove any candidates.
        If the cell has no candidates, it will raise an error.

        Raises a ValueError if the cell no longer has any candidates.
        """
        if self.value:
            return 0

        current_candidates = self.candidates.copy()
        self.candidates -= set_to_remove
        self.validate()
        return abs(len(self.candidates) - len(current_candidates))

    def guarantee_candidates(self, pro_set: set) -> int:
        """
        Removes candidates from the cell that are not in the pro_set
        Returns 1 if the candidates were changed, 0 if not
        """
        if self.value:
            return

        temp = self.candidates.copy()

        # & is the intersection operator
        self.candidates &= pro_set

        if self.candidates == temp:
            return 0
        return abs(len(self.candidates) - len(temp))

    def validate(self):
        """
        Raises a ValueError if the cell has no candidates, and no value
        """
        if not (self.value or len(self.candidates) > 0):
            raise ValueError(f"Cell {self.row}, {self.col} has no candidates")


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

    def add_cell(self, cell: Cell) -> None:
        """
        Adds a cell to the cluster
        Updates the values set with the value of the cell

        Raises a ValueError if the value is already in the cluster
        Raises a ValueError if the cluster already has 9 cells
        """
        if cell.value in self.values:
            raise ValueError(f"Value {cell.value} already in cluster")

        if len(self.cells) == 9:
            raise ValueError("Cluster already has 9 cells")

        self.cells.append(cell)
        if cell.value:
            self.values.add(cell.value)

        if len(self.cells) == 9:
            self.update_candidates()
        return

    def update_candidates(self) -> None:
        """
        Makes sure that all cell values have been added to the values set
        Eliminates all candidates that are in the values set
        """
        dup_check = set()
        for cell in self.cells:
            if not cell.value:
                continue

            if cell.value not in self.values:
                self.values.add(cell.value)

            if cell.value not in dup_check:
                dup_check.add(cell.value)
            else:
                raise ValueError(f"Duplicate value {cell.value} in cluster")

        for cell in self.cells:
            cell.remove_candidates(self.values)


class Board:
    def __init__(self, data: list, raw_data=False):
        self.cells = [[Cell(i, j) for j in range(9)] for i in range(9)]
        self.rows = [Cluster() for _ in range(9)]
        self.cols = [Cluster() for _ in range(9)]
        self.boxs = [Cluster() for _ in range(9)]
        self.solved_cells = 0

        if raw_data:
            self.format_data(data)

        self.populateData(data)

    def format_data(self, data):
        for row in range(9):
            for col in range(9):
                if data[row][col] == ".":
                    data[row][col] = 0
                else:
                    data[row][col] = int(data[row][col])

    def as_data(self):
        data = []
        for row in self.cells:
            row_data = []
            for cell in row:
                row_data.append(cell.value)
            data.append(row_data)
        return data

    def populateData(self, board) -> None:
        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    self.cells[row][col].set_val(int(board[row][col]))
                    self.solved_cells += 1

                cell = self.cells[row][col]
                self.rows[row].add_cell(cell)
                self.cols[col].add_cell(cell)
                self.boxs[cell.box].add_cell(cell)
        return

    def printPretty(self):
        for row in self.cells:
            for cell in row:
                print(cell, end=" ")
            print()

    def printCandidates(self):
        output = [[" " for _ in range(27)] for _ in range(27)]

        for row in range(9):
            for col in range(9):
                start_row, start_col = row * 3, col * 3

                if self.cells[row][col].value:
                    num = str(self.cells[row][col])
                    output[start_row + 1][start_col + 1] = num
                else:
                    for candidate in self.cells[row][col].candidates:
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

    def set_cell(self, val, cell):
        cell.set_val(val)
        self.update_candidates(cell)
        return

    def update_candidates(self, cell: Cell) -> None:
        self.rows[cell.row].update_candidates()
        self.cols[cell.col].update_candidates()
        self.boxs[cell.box].update_candidates()


class SudokuSolver:
    def __init__(self, data: list):
        self.board = Board(data)

    def solve(self):
        try:
            return self.__solve()
        except ValueError:
            return -1

    def __solve(self):
        changed = 1
        while changed:
            changed = 0
            changed += self.naked_singles()
            if changed:
                continue

            changed += self.funcToAllClusters(self.hiddenSingle)
            if changed:
                continue

            changed += self.funcToAllClusters(self.nakedDouble)
            if changed:
                continue

            changed += self.funcToAllClusters(self.hiddenDouble)
            if changed:
                continue

        if self.is_solved():
            return 1

        return self.dfs()

    def is_solved(self):
        solved_cells = 0
        for row in self.board.cells:
            for cell in row:
                if cell.value:
                    solved_cells += 1
        if solved_cells == 81:
            return True
        return False

    def naked_singles(self):
        changed = 0
        for row in self.board.cells:
            for cell in row:
                if len(cell.candidates) == 1:
                    self.board.set_cell(cell.candidates.pop(), cell)
                    changed += 1
        return changed

    def hiddenSingle(self, cluster):
        """
        Hidden single is when a cell doesn't have a value, but it has the only
        instance of that candidate in the cluster.

        Example: (1, 2, 3), (2, 3), and (2, 3) are the last 3 cells in a row.
        The first cell MUST be a 1.
        """
        changed = False
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
                if self.board.set_cell(candidate.pop(), cell):
                    changed = True
        return changed

    def nakedDouble(self, cluster):
        """
        Similar to a naked single but a little trickier.
        When two cells have 2 candidates that are identical, no other cells
        in that cluster can contain those numbers. We can actually use
        the example from hidden single to also deduce the 1.

        Example: (1, 2, 3), (2, 3), and (2, 3) are the last 3 cells in a row.
        This means the first cell cannot have a 2, or 3 in it because the
        second and third cell must be 2 or 3.
        """
        count = 0
        for i in range(9):
            if len(cluster.cells[i].candidates) == 2:
                for j in range(i + 1, 9):
                    if cluster.cells[i].candidates == cluster.cells[j].candidates:
                        for k in range(9):
                            if k == i or k == j:
                                continue
                            count += cluster.cells[k].remove_candidates(
                                cluster.cells[i].candidates
                            )
        return count

    def hiddenDouble(self, cluster):
        """
        If two cells are the only two cells to contain those numbers in a cluster,
        it's a hidden double.

        Example: (1, 5, 3, 6), (1, 5, 3), (1, 3, 4, 5, 8), (3, 4, 5, 6, 8)
        The last two cells are the only ones with 4 and 8, those cells must be
        4 or 8, so it becomes

        (1, 5, 3, 6), (1, 5, 3), (4, 8), (4, 8)
        """
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
                        if i in cand_map[key]:
                            count += cluster.cells[i].guarantee_candidates({key, key2})

        return count

    def funcToAllClusters(self, func):
        """
        This runs a function to all clusters on the board.

        It does not catch any errors, errors are to be caught by solve method.
        """
        count = 0
        for row in self.board.rows:
            count += func(row)
        for col in self.board.cols:
            count += func(col)
        for box in self.board.boxs:
            count += func(box)
        return count

    def remainingCombinations(self):
        """
        Purely for debugging and fun.
        Shows the product of all the remaining candidates of the board.
        """
        combos = 1
        for row in self.board:
            for cell in row:
                if not cell.value:
                    combos *= len(cell.candidates)
        return combos

    def cell_with_fewest_candidates(self):
        """
        Returns the cell with the fewest candidates.
        """
        min_cell = None
        min_candidates = 10
        for row in self.board.cells:
            for cell in row:
                if not cell.value and len(cell.candidates) < min_candidates:
                    min_cell = cell
                    min_candidates = len(cell.candidates)
        return min_cell


    def dfs(self):
        """
        Time to brute force the solution.
        """
        cell = self.cell_with_fewest_candidates()
        for candidate in cell.candidates:
            board_copy = self.board.as_data()
            board_copy[cell.row][cell.col] = candidate
            solver = SudokuSolver(board_copy)
            if solver.solve() == -1:
                continue
            self.board = solver.board
            return 1
        return -1


if __name__ == "__main__":
    board = sys.stdin.read()
    board = [list(row.strip()) for row in board.split("\n")]
    if board[-1] == []:
        board.pop()
    solver_board = Board(board, raw_data=True)
    board = solver_board.as_data()
    solver = SudokuSolver(board)
    solver.board.printPretty()
    solver.solve()
    print()
    solver.board.printPretty()

'''

class SudokuSolver:
    """
    Contains all the logic for solving a Sudoku board.

    board:      A 9x9 list of Cell objects
    rows:       A list of 9 Cluster objects representing the rows
    cols:       A list of 9 Cluster objects representing the columns
    boxs:       A list of 9 Cluster objects representing the boxes

    populateData:           Populates the board with the given board
    initializeCandidates:   Initializes the candidates of all cells in the board
    boardToList:            Converts the board to a 9x9 list of integers
    getBox:                 Returns the box of the cell at (row, col)
    printCandidates:        Prints the candidates of all cells in the board
    solve:                  Solves the board
    printPretty:            Prints the board in a readable format (not candidates)
    """

    def __init__(self, board: list):
        self.board = [[Cell(i, j) for j in range(9)] for i in range(9)]

        self.rows = [Cluster() for _ in range(9)]
        self.cols = [Cluster() for _ in range(9)]
        self.boxs = [Cluster() for _ in range(9)]
        self.solved = 0

        self.populateData(board)
        self.initializeCandidates()

    def __str__(self):
        string = []
        for row in self.rows:
            string.append(str(row))
        return "\n".join(string)



    def initializeCandidates(self):
        for row in self.rows:
            row.initializeCandidates()
        for col in self.cols:
            col.initializeCandidates()
        for box in self.boxs:
            box.initializeCandidates()

    def boardToList(self):
        board = []
        for row in self.board:
            board.append([cell.value for cell in row])
        return board

    def getBox(self, row, col):
        return (row // 3) * 3 + col // 3



    def solve(self):
        changed = 1
        while changed:
            changed = 0
            if self.nakedSingles():
                changed = 1
                continue

            if self.funcToAllClusters(self.hiddenSingle):
                changed = 1
                continue

            if self.funcToAllClusters(self.nakedDouble):
                changed = 1
                continue

            if self.funcToAllClusters(self.hiddenDouble):
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
        cell = self.firstUnsolvedCell()

        for candidate in self.board[cell[0]][cell[1]].candidates:
            print(f"Trying {candidate} at {cell}")
            print("Remaining Combinations:", self.remainingCombinations())
            board_copy = self.boardToList()
            board_copy[cell[0]][cell[1]] = candidate
            solver = SudokuSolver(board_copy)
            if solver.solve() == -1:
                print(f"Failed with {candidate} at {cell}")
                continue

            self.board = solver.board

        return 1

    def firstUnsolvedCell(self):
        """
        Finds the first unsolved cell in the board in row major order.
        This should be optimized to find the piece with the lowest number
        of candidates.
        """
        for row in range(9):
            for col in range(9):
                if not self.board[row][col].value:
                    return (row, col)







'''
