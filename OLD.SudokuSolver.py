import sys


class Verbose:
    verbose = False

    def turn_on(self):
        Verbose.verbose = True

    def print(self, *args):
        if Verbose.verbose:
            print(*args)


class Cell:
    """
    Contains all the logic for a single cell in the Sudoku Board.
    All rows, columns, and boxes are 0-indexed.

    row:        The row of the cell
    col:        The column of the cell
    box:        The box of the cell (0 being the top left, 8 being the bottom right)
    candidates: A set of all possible values the cell could be.
    value:      The value of the cell. 0 if the cell is empty.
    marked:     A boolean value to determine if the cell has been marked for an operation.

    eliminateCandidates:    Removes candidates from the cell that are in the anti_set
    guaranteeCandidates:    Removes candidates from the cell that are not in the pro_set
    setVal:                 Sets the value of the cell to val
    """

    def __init__(self, row: int = -1, col: int = -1, value: int = 0):
        self.row = row
        self.col = col
        self.box = (row // 3) * 3 + col // 3

        self.value = value
        self.candidates = {1, 2, 3, 4, 5, 6, 7, 8, 9}

        if value:
            self.candidates.clear()

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"{self.value}"

    def setVal(self, val) -> None:
        """
        Sets the value of the cell to val
        Removes all candidates from the cell
        Returns nothing
        """
        self.value = val
        self.candidates = set()
        return

    def eliminateCandidates(self, anti_set: set) -> int:
        """
        Removes candidates from the cell that are in the anti_set
        Returns 1 if the candidates were changed, 0 if not
        """
        if self.value:
            return 0

        temp = self.candidates.copy()
        self.candidates -= anti_set
        if self.candidates == temp:
            return 0

        return 1

    def guaranteeCandidates(self, pro_set: set) -> int:
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
        return 1


class Cluster:
    """
    Contains all the logic for a row, column or box in the Sudoku Board.
    Each cluster should have references to all the cells in the cluster.
    When a cell is modified, it should be updated in ALL 3 clusters it belongs
    to.

    cells:  A list of all the cells in the cluster
    values: A set of all the values in the cluster

    addCell:                Adds a cell to the cluster
    setCell:                Sets the value of the cell at cell_idx to val
    """

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

    def addCell(self, cell: Cell) -> None:
        """
                Adds a cell to the cluster
                Updates the values set with the value of the cell
        l
                *** DOES NOT UPDATE CANDIDATES ***
        """
        self.cells.append(cell)
        if cell.value:
            self.values.add(cell.value)

    def setCell(self, val: int, cell_idx: int):
        """
        Sets the value of the cell at cell_idx to val
        Updates the candidates of all cells in the cluster
        Returns True if the remaining candidates are valid, False if not
        """
        self.raiseIfAlreadyInCluster(val)
        self.cells[cell_idx].setVal(val)
        self.updateCandidates()

        self.raiseIfEmptyCandidates()
        return

    def initializeCandidates(self) -> None:
        """
        Initializes the candidates of all cells in the cluster
        This assumes that all cells have been added to the cluster
        """
        for cell in self.cells:
            cell.eliminateCandidates(self.values)

    def updateCandidates(self) -> None:
        """
        Makes sure that all cell values have been added to the values set
        Eliminates all candidates that are in the values set
        """
        for cell in self.cells:
            if cell.value not in self.values:
                self.values.add(cell.value)

        for cell in self.cells:
            cell.eliminateCandidates(self.values)

    def raiseIfAlreadyInCluster(self, val: int) -> None:
        """
        Raises a ValueError if the value is already in the cluster
        """
        if val in self.values:
            raise ValueError("Value already in cluster")

    def raiseIfEmptyCandidates(self):
        """
        Validates that all cells in the cluster have valid candidates
        Returns True if all non-solved cells have candidates, False if not
        """
        for cell in self.cells:
            if not cell.value and not cell.candidates:
                raise ValueError("Invalid board")


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

    def populateData(self, board) -> None:
        for row in range(9):
            for col in range(9):
                if board[row][col] != "." and board[row][col] != 0:
                    self.board[row][col].setVal(int(board[row][col]))

                self.rows[row].addCell(self.board[row][col])
                self.cols[col].addCell(self.board[row][col])
                self.boxs[self.getBox(row, col)].addCell(self.board[row][col])
        return

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

    def printPretty(self):
        """
        Prints the board in a readable format (no candidates)
        9x9 grid of numbers.
        """
        for row in self.board:
            for cell in row:
                print(cell, end=" ")
            print()

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

    def setCell(self, val, cell):
        """
        Sets the value of the cell to val
        Updates the candidates of all cells in the cluster
        Returns True if the remaining candidates are valid, False if not

        Note: This method might throw an error if the value is already in the cluster.
        Note: This method might throw an error if there is now a totall empty cell.

        This error will be resolved in the "solve" method.
        """
        cell.setVal(val)
        self.rows[cell.row].updateCandidates()
        self.cols[cell.col].updateCandidates()
        self.boxs[cell.box].updateCandidates()
        return

    def funcToAllClusters(self, func):
        """
        This runs a function to all clusters on the board.

        It does not catch any errors, errors are to be caught by solve method.
        """
        count = 0
        for row in self.rows:
            count += func(row)
        for col in self.cols:
            count += func(col)
        for box in self.boxs:
            count += func(box)
        return count

    def nakedSingles(self) -> int:
        """
        A naked single is when a cell doesn't have a value, but it has a single
        candidate.

        It does not catch errors from "setCell" that happens in the solve method.
        """
        changed = False
        for row in self.rows:
            for cell in row.cells:
                if len(cell.candidates) == 1:
                    if self.setCell(cell.candidates.pop(), cell):
                        changed = True
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
                if self.setCell(candidate.pop(), cell):
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
                            count += cluster.cells[k].eliminateCandidates(
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
                            count += cluster.cells[i].guaranteeCandidates(
                                {key, key2})

        return count


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        Verbose().turn_on()
        print("Verbose mode turned on")

    board = sys.stdin.read()
    board = [list(row.strip()) for row in board.split("\n")]
    if board[-1] == []:
        board.pop()
    solver = SudokuSolver(board)
    solver.solve()
    solver.printCandidates()
    print("Remaining combinations:", solver.remainingCombinations())
