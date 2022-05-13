"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    Xcount = 0
    Ocount = 0

    for row in board:
        Xcount += row.count(X)
        Ocount += row.count(O)

    if Xcount <= Ocount:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    possible_moves = set()  # Initializes a set to store the possible moves 
    for row in range(len(board)):  
        for col in range(len(board)):  # Loops over board
            if board[row][col] == EMPTY:  # Checks if a box/position is empty
                possible_moves.add((row, col))  # If the position is Empty it gets added to the set possible moves

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    move_by_player = player(board)  # Storing the player move
    new_board = deepcopy(board)  # Making a deep copy of the board
    (i, j) = action
    if board[i][j] != None:  # Checking if the move is valid
        raise Exception
    else:
        new_board[i][j] = move_by_player  # Adding the move to the new board

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for player in (X, O):
            for row in board:
                if row == [player] * 3:  # Checks horizontally to see if a row is filled
                    return player

            for i in range(3):
                column = [board[x][i] for x in range(3)]
                if column == [player] * 3:  # Checks vertically to see if a row is filled
                    return player

            if [board[i][i] for i in range(0, 3)] == [player] * 3:
                return player

            elif [board[i][~i] for i in range(0, 3)] == [player] * 3:  # Checks diagonally to see if a row is filled
                return player
    return None
                               

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:  # Returns true if someone wins
        return True
    for row in board:  # Returns False if there are still moves to play
        if EMPTY in row:
            return False
    return True  # Returns true if no possible moves are remaining


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    win = winner(board)  # Stores the winner of the game in the win variable
    if win == X:  # Check if X has won
        return 1
    elif win == O:  # checks if O has won
        return -1
    else:
        return 0  # Returns 0 if no one wins


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    def max(board):
        best_move = ()
        if terminal(board):
            return utility(board), best_move
        else:
            v = -5
            for action in actions(board):
                minval = min(result(board, action))[0]
                if minval > v:
                    v = minval
                    best_move = action
            return v, best_move

    def min(board):
        best_move = ()
        if terminal(board):
            return utility(board), best_move
        else:
            v = 5
            for action in actions(board):
                maxval = max(result(board, action))[0]
                if maxval < v:
                    v = maxval
                    best_move = action
            return v, best_move

    now_playing = player(board)

    if terminal(board):
        return None
    if now_playing == X:
        return max(board)[1]
    else:
        return min(board)[1]