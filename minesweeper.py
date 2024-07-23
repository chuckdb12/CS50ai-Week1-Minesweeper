import itertools
import random


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
        # The only way to know for sure that a cell is a mine, is if the lenght of the sentence is the same as the count
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # 1.First check if the cell is part of self.cells
        if cell in self.cells:
            
            # 2. Remove the cell form the sentence
            self.cells.remove(cell)
            # Remove a count because there is one less mine in the set
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
       # 1.First check if the cell is part of self.cells
        if cell in self.cells:
            
            # 2. Remove the cell form the sentence
            self.cells.remove(cell)
            # In this case, we do not modify the count because there are still as many mines in the set


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
        #self.knowledge: list[Sentence] = []

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
        # 1)Add cell to move made
        self.moves_made.add(cell)
        # 2)Mark cell as safe
        self.mark_safe(cell)
        # 3)add new sentence to the AI KB
        # 3.1) Lets first create the set of all the cell's neighbors
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # We don't want to add the cell itself
                if (i, j) == cell:
                    continue
                
                # IF the cell is inside the board, we add it to the neighbors set()
                
                if 0 <= i < self.height and 0 <= j < self.width:

                    #If the cell is known to be a mine, we decrease the count and do not add it to the set
                    if ((i, j) in self.mines):
                        count -= 1
                        continue

                    #If the cell is not marked as safe, we add it to the set
                    if not((i, j) in self.safes):
                        neighbors.add((i, j))

        # Creation of the new sentence
        newSentence = Sentence(neighbors, count)
        # Let's add this new sentence to the KB
        self.knowledge.append(newSentence)

        # 4 Mark any additional cells as safe of as mines

        for sentence in self.knowledge:
            # Creation of a set which will contain only mines if created
            mines = sentence.known_mines()
            # Same principle for safe cells
            safes = sentence.known_safes()
            if mines:
                #Iterating on a copy of the set to avoid potential errors
                for cell in mines.copy():
                    self.mark_mine(cell)
            elif safes:
                for cell in safes.copy():
                    self.mark_safe(cell)

        # We now need to delete any sentence that would be empty
        # To do so, list comprehension will be used : https://www.w3schools.com/python/python_lists_comprehension.asp

        #Creation of an empty sentence to be compared
        #emptySentence = Sentence(set(), 0)

        self.knowledge = [sentence for sentence in self.knowledge if sentence != Sentence(set(), 0)]

        # 5.1 Lets check if the new sentence is a subset of any existing sentences in the KB

        for subSetSentence in self.knowledge:
            for superSetSentence in self.knowledge:
            # If the subSetSentence is a subset of superSetSentence, we can inffer a new sentence
                if subSetSentence.cells < superSetSentence.cells:
                    infferedCells = superSetSentence.cells - subSetSentence.cells
                    infferedCount = superSetSentence.count - subSetSentence.count
                    infferedSentence = Sentence(infferedCells, infferedCount)
                    # Add the new sentence to the KB if not already there
                    if infferedSentence not in self.knowledge:
                        self.knowledge.append(infferedSentence)
                
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # We first look is there are known safe cells, and then check if one of these cells has not been played yet
        if len(self.safes) > 0:
            for cell in self.safes:
                if cell not in self.moves_made:
                    return cell
        # Otherwise, return None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #Create a set of eventual possible moves
        eventualMoves = set()
        for i in range(0, self.height):
            for j in range(0, self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    #If (i, j) is has not been played yet and is not known to be a mine, we return it
                    eventualMoves.add((i, j))

        if len(eventualMoves) == 0:
            return None
        else:
            return eventualMoves.pop()


"""
        while True:
            i = random.randint(0, self.width - 1)
            j = random.randint(0, self.height - 1)
            if (i, j) not in self.moves_made:
                if (i, j) not in self.mines:
                    #If (i, j) is has not been played yet and is not known to be a mine, we return it
                    return (i, j)
        
"""
