import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("â–ˆ", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        deepcopy_domain = copy.deepcopy(self.domains)
        for var in self.domains:  # Checking every variable in domain
            leng = var.length  
            for words in deepcopy_domain[var]:  # Checking whether the words and the variable are same length

                if len(words) != leng:
                    self.domains[var].remove(words)  # If there are not the same length it will removed from the domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap_x, overlap_y = self.crossword.overlaps[x, y]  # Assigning overlapping cells to vaariables
        revision = False  # Revision status
        copy_domain = copy.deepcopy(self.domains)  # Deep copy of Domain

        if overlap_x:  # If overlap happens
            for word_x in copy_domain[x]:
                match = False  # Initiliaze a variable to check if math is found or not
                for word_y in self.domains[y]:
                    if word_x[overlap_x] == word_y[overlap_y]:
                        match = True  # If a match has been found it return True
                        break
                if match:
                    continue  # Iterates through X's domain again
                else:
                    self.domains[x].remove(word_x)  # If there isn't a match then it will that word from X's domain
                    revision = True  # And returns True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = [] 
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if self.crossword.overlaps[var1, var2] is not None:
                        queue.append((var1, var2))  # Populate the queue with all the arcs

        while len(queue) > 0:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbour in self.crossword.neighbors(x):
                    if neighbour != y:
                        queue.append((neighbour, x))
            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        word = [*assignment.values()]
        if len(word) != len(set(word)):
            return False  # Check if all the values are different

        for var in assignment:
            if var.length != len(assignment[var]):  # Checking whether they are correct length
                return False

        for var in assignment:
            for n in self.crossword.neighbors(var):
                if n in assignment:
                    x, y = self.crossword.overlaps[var, n]         # Checks any conflicts between the neighbouring variables
                    if assignment[var][x] != assignment[n][y]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        DictWord = {}  # Initiliaze a dictionary
        neighbours = self.crossword.neighbors(var)  # Takes the neighbours
        for words in self.domains[var]:
            removed = 0
            for n in neighbours:
                if n in assignment:
                    continue
                else:
                    overlap_x, overlap_y = self.crossword.overlaps[var, n]  # Checks if the neighbour and word overlaps
                    for n_word in self.domains[n]:  
                        if words[overlap_x] != n_word[overlap_y]:  # Loops through neighbour's words and checks for eliminated ones
                            removed = removed + 1 
            DictWord[words] = removed
            # Variables sorted in dictionary by the no.of eliminated neighbour values
            sorted_l = {k: v for k, v in sorted(DictWord.items(), key=lambda item: item[1])}
            return [*sorted_l]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        unassign_var = {}  # Initiliaze a dictionary

        for var in self.domains:
            if var not in assignment:  # If a variable is not assignment 
                unassign_var[var] = self.domains[var]  # It becomes a part of our dict

          # Creates a list of variables sorted by no.of remaining values    
        sorted_l = [v for v, k in sorted(unassign_var.items(), key=lambda item:len(item[1]))]
        return sorted_l[0] 

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.domains):  # If assigment is done
            return assignment

        var = self.select_unassigned_variable(assignment)  # Select a unassigned variable

        for value in self.domains[var]:  # Looping over words in that variable
            copy_assign = assignment.copy()  # Assignment copy with the new variable value
            copy_assign[var] = value
            if self.consistent(copy_assign):  # Checks for consistency
                result = self.backtrack(copy_assign)  # Result of the new assignment backtrack
                if result is not None:
                    return result
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()