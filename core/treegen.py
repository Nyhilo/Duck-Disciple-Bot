from typing import List
from enum import Enum
from random import choices, choice


class Cell():
    _order = 0

    def __init__(self, x: int, y: int, feature: str = " ") -> None:
        self.x = x
        self.y = y
        self.feature = feature

        # An internal sequential id used for potential animation purposes
        self._order += 1
        self.order = self._order


class Option(Enum):
    Nothing = 1
    Leaf = 2
    Grow = 3
    Bud = 4
    Flower = 5
    Bifurcate = 6


class Branch():
    def __init__(self, base: Cell, parent: "Branch" = None) -> None:
        self.base = base
        self.tip = base
        self.cells: List[Cell] = [base]
        self.parent = parent

        # Base level branches have a nesting level of 1, and increase as we... branch out
        self.nesting = 1 if parent is None else parent.nesting + 1

    def add_tip(self, cell: Cell) -> None:
        self.cells.append(cell)
        self.tip = cell

    def random_segment(self) -> Cell:
        return choice(self.cells)


class Plant_Type_1():
    def __init__(self) -> None:
        origin = Cell(0, 0, '|')
        self.grid = {0: {0: origin}}
        self.trunk = Branch(origin)
        self.branches = [self.trunk]

    def get_cell(self, x: int, y: int) -> Cell:
        row = self.grid.get(x)
        cell = None if row is None else row.get(y)
        # Create a new cell in that location if it doesn't exist
        if cell is None:
            cell = Cell(x, y)

        return cell

    def set_cell(self, cell: Cell) -> None:
        if cell.x not in self.grid:
            self.grid[cell.x] = {}

        self.grid[cell.x][cell.y] = cell

    def generate(self, iterations: int) -> None:
        for i in range(iterations):
            self.iterate(i)

    def iterate(self, iteration: int) -> None:
        branch = self.select_branch()
        option = self.select_growth()

        if option == Option.Nothing:
            pass

        elif option == Option.Leaf:
            segment = branch.random_segment()
            adjacent = self.select_random_adjacent(segment)
            if adjacent is not None:
                adjacent.feature = '&'
                self.set_cell(adjacent)

        elif option == Option.Grow:
            pass

        elif option == Option.Bud:
            segment = branch.random_segment()
            adjacent = self.select_random_adjacent(segment)
            if adjacent is not None:
                adjacent.feature = '°'
                self.set_cell(adjacent)

        elif option == Option.Flower:
            pass

        elif option == Option.Bifurcate:
            pass

    def select_branch(self) -> Branch:
        return choices(self.branches, weights=[branch.nesting for branch in self.branches])

    def select_growth(self) -> Option:
        pool_weights = [4, 3, 2, 2, 2, 1]
        return choices(list(Option), weights=pool_weights)

    def select_random_adjacent(self, cell: Cell) -> Cell:
        valid_adjacent_cells = []

        # Find empty cells that are adjacent to the cell
        if cell.feature == '|':
            adjacent_cells = [self.get_cell(cell.x-1, cell.y),
                              self.get_cell(cell.x+1, cell.y)]
            valid_adjacent_cells = [c for c in adjacent_cells if c.feature == " "]

        elif cell.feature == '-':
            adjacent_cells = [self.get_cell(cell.x, cell.y+1),
                              self.get_cell(cell.x, cell.y-1)]
            valid_adjacent_cells = [c for c in adjacent_cells if c.feature == " "]

        elif cell.feature == '/' or cell.feature == '\\':
            adjacent_cells = [self.get_cell(cell.x-1, cell.y),
                              self.get_cell(cell.x, cell.y+1),
                              self.get_cell(cell.x+1, cell.y),
                              self.get_cell(cell.x, cell.y-1)]
            valid_adjacent_cells = [c for c in adjacent_cells if c.feature == " "]

        # Sometimes the realestate around a cell is saturated
        if len(valid_adjacent_cells) == 0:
            return None

        return choice(valid_adjacent_cells)
