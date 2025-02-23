class Player:
    """Base player class"""
    def __init__(self, symbol):
        self.symbol = symbol

    def get_symbol(self):
        return self.symbol
    
    # probably can delete this when we implement get_move() Not sure though
    def get_move(self, board):
        raise NotImplementedError()



class HumanPlayer(Player):
    """Human subclass with text input in command line"""
    def __init__(self, symbol):
        Player.__init__(self, symbol)
        self.total_nodes_seen = 0

    def clone(self):
        return HumanPlayer(self.symbol)
        
    def get_move(self, board):
        col = int(input("Enter col:"))
        row = int(input("Enter row:"))
        return  (col, row)


class AlphaBetaPlayer(Player):
    """Class for Alphabeta AI: implement functions minimax, eval_board, get_successors, get_move
    eval_type: int
        0 for H0, 1 for H1, 2 for H2
    prune: bool
        1 for alpha-beta, 0 otherwise
    max_depth: one move makes the depth of a position to 1, search should not exceed depth
    total_nodes_seen: used to keep track of the number of nodes the algorithm has seearched through
    symbol: X for player 1 and O for player 2
    """
    def __init__(self, symbol, eval_type, prune, max_depth):
        Player.__init__(self, symbol)
        self.eval_type = int(eval_type)
        self.prune = prune
        self.max_depth = int(max_depth) 
        self.max_depth_seen = 0
        self.total_nodes_seen = 0
        if symbol == 'X':
            self.oppSym = 'O'
        else:
            self.oppSym = 'X'


    def terminal_state(self, board):
        # If either player can make a move, it's not a terminal state
        for c in range(board.cols):
            for r in range(board.rows):
                if board.is_legal_move(c, r, "X") or board.is_legal_move(c, r, "O"):
                    return False 
        return True 


    def terminal_value(self, board):
        # Regardless of X or O, a win is float('inf')
        state = board.count_score(self.symbol) - board.count_score(self.oppSym)
        if state == 0:
            return 0
        elif state > 0:
            return float('inf')
        else:
            return -float('inf')


    def flip_symbol(self, symbol):
        # Short function to flip a symbol
        if symbol == "X":
            return "O"
        else:
            return "X"


    # Gets all 
    def alphabeta(self, board):
        # best_move = (val, col, row)
        best_move = self.max_val(board, float('-inf'), float('inf'), self.max_depth)
        return best_move[1], best_move[2]
    

    def max_val(self, board, a, b, d):
        if self.terminal_state(board):
            return self.terminal_value(board), None, None
        if d == 0:
            return self.eval_board(self, board), None, None
        
        d -= 1 # Decrement Depth

        successors = self.get_successors(board, self.symbol)
        best_move = (None, None, None)
        for s, r, c in successors: 
            val = None
            if self.terminal_state(s):
                val = self.terminal_value(s)
            else:
                val = self.min_val(s, a, b, d)
            # Chooses successor if it's score is larger than all previous successors
            if val > a:
                a = val
                best_move = (r, c)

        return a, best_move[0], best_move[1]
        


    def min_val(self, board, a, b, d):
        if self.terminal_state(board):
            return self.terminal_value(board)
        if d == 0:
            return self.eval_board( board)
        
        d -= 1

        successors = self.get_successors(board, self.symbol)
        for s, _, _ in successors: 
            val = None
            if self.terminal_state(s):
                val = self.terminal_value(s)
            else:
                val, _, _ = self.max_val(s, a, b, d)
            
            # Prunes, no other branches in this min node will be checked
            if val < a: 
                return val
            
            # Updates beta value of node if it fines a lower value move
            if val < b: 
                b = val
        return b



    def eval_board(self, board):
        # type: (board) -> (float)
        # check if terminal state
        if self.terminal_state(board) :
            return self.terminal_value(board)
        value = 0
        if self.eval_type == 0:
            #print("eval_type = 0") # Testing purposes only
            # should return number of player pieces - number of opponenets pieces
            value = board.count_score(self.symbol) - board.count_score(self.oppSym) 
        elif self.eval_type == 1:
            #print("eval_type = 1") # Testing purposes only
            # should return number of player legal moves - number of opponents legal moves
            player_legal_moves, opp_legal_moves = 0, 0
            for c in range(0, board.get_num_cols()):
                for r in range(0, board.get_num_rows()):
                    if board.is_legal_move(c, r, self.symbol) : player_legal_moves += 1 
                    if board.is_legal_move(c, r, self.oppSym) : opp_legal_moves += 1 
            value = player_legal_moves - opp_legal_moves
        elif self.eval_type == 2:
            #print("eval_type = 2") # Testing purposes only
            # Design own heuristic
            value = 2
        return value


    def get_successors(self, board, player_symbol):
        # Write function that takes the current state and generates all successors obtained by legal moves
        # type:(board, player_symbol) -> (list)
        successors = [] 
        # check if no valid moves
        if not board.has_legal_moves_remaining(player_symbol):
            return successors 

        for c in range(0, board.get_num_cols()):
            for r in range(0, board.get_num_rows()):
                if board.is_legal_move(c, r, player_symbol):
                    new_board = board.cloneOBoard() # clone current board
                    new_board.play_move(c, r, player_symbol) # sometimes there is an invalid move somehow
                    successors.append((new_board, c, r)) # play move and save board state to successors
        
        # for b in successors: # temp test to print all successor boards
        #     b.display()
        #     print(self.eval_board(b))
    
        return successors # list of possible next board states (empty if none)


    def get_move(self, board):
        # Write function that returns a move (column, row) here using minimax
        # type:(board) -> (int, int)
        return self.alphabeta(board)

       
        





