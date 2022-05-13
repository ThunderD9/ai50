import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):  # if the count/number(mines) is equal to the cells then we know they are mines
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:  # If the count/number is equal 0 then they are known as safes
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        else:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        #1
        self.moves_made.add(cell)  # Marking the cell as a move that has been made

        #2
        if cell not in self.safes:
            self.mark_safe(cell)  # Marking the cell as safe


        cells = set()  # Creating a set to add unknown states
        count_copy = copy.deepcopy(count)  # Creating a deep copy of count/mines
        close_cells = self.neighbour(cell)  # Returns the neighbouring cells
        for a_cell in close_cells:  # For a cell in Neighbouring cell
            if a_cell in self.mines:  # If it is mines
                count_copy -= 1  # Decrement the count
            if a_cell not in self.mines | self.safes:  # If the cell is not in mines or safes
                cells.add(a_cell)  # Then add that cell to our set

        new_sentence = Sentence(cells, count_copy)  # Create new sentence by using the new cells and count copy

        if len(new_sentence.cells) > 0:  # Only add the new sentence to our knowledge,if it is not empty
            self.knowledge.append(new_sentence)  # Appending the new sentence to our knowledge base

        self.check_knowledge()  # Calling our knowledge function

        self.extra_inference()  # Calling our inference function

    def neighbour(self, cell):  # Gives out the cells close to the given cell by 1 cell
        """
        returns cell that are 1 cell away from cell passed in arg
        """
        neighbours = set()
        for rows in range(self.height):
            for columns in range(self.width):  # For each cell
                if abs(cell[0] - rows) <= 1 and abs(cell[1] - columns) <= 1 and (rows, columns) != cell:  # Figures out the neighbours
                    neighbours.add((rows, columns))  # Add the neighbour cells to the set
        return neighbours

    def check_knowledge(self):
        """
        check knowledge for new safes and mines, updates knowledge if possible
        """
        knowledge_copy = copy.deepcopy(self.knowledge)  # Making a deep copy of our knowledge

        for sentence in knowledge_copy:  # Loops through every sentence from our knowledge copy
            if len(sentence.cells) == 0:
                try:
                    self.knowledge.remove(sentence)  # If the sentence contains nothing then it will remove it from our knowledge base
                except ValueError:
                    pass

            mines = sentence.known_mines()  # Checks for possible mines
            safes = sentence.known_safes()  # Checks for possible safes

            if mines:
                for mine in mines:
                    self.mark_mine(mine)  # Marking it as mine
                    self.check_knowledge()  # Checking the knowledge with updated knowledge/mine
            if safes:
                for safe in safes:
                    self.mark_safe(safe)  # Marking it as safe
                    self.check_knowledge()  # Checking the knowledge with updated knowledge/safe

    def extra_inference(self):
        """
        update knowledge based on inference
        """
        for sen1 in self.knowledge:
            for sen2 in self.knowledge:  # Looping over pairs of sentences
                if sen1.cells.issubset(sen2.cells):  # Checking if a sentence is subset of another
                    cells_now = sen2.cells - sen1.cells  # If it is subset then cells in a new set is cells which are not in the subset
                    count_now = sen2.count - sen1.count  # If it is subset then count/mines in a new set is count/mines which are not in the subset
                    new_sentence = Sentence(cells_now, count_now)  # New sentence consists of new_cells and new_count
                    mines = new_sentence.known_mines()  # Checks for possible mines
                    safes = new_sentence.known_safes()  # Checks for possible safes
                    if mines:
                        for mine in mines:
                            self.mark_mine(mine)  # Marking it as mine

                    if safes:
                        for safe in safes:
                            self.mark_safe(safe)  # Marking it as safe

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for moves in self.safes - self.moves_made: # For a move which is in safe but not in moves_made
            return moves  # Make that move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        possible_moves = self.width * self.height  # Calculating total possible moves
        while possible_moves > 0:
            possible_moves = possible_moves - 1  # Decrementing our possible moves by 1

            row = random.randrange(self.width)  # Selecting a Random row
            column = random.randrange(self.height)  # Selecting a Random Column

            if (row, column) not in self.moves_made | self.mines:
                return (row, column)
        return None