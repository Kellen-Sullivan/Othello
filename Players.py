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
        self.eval_board(board) # TEMP PRINT STATEMENT
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
        # (board) -> (float)
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
            """
            Note: 'stable' pieces are pieces that can't be flipped (corners are stable)
            Own heuristic first counts the number of 'stable' peices. Then it sums 
            the number of stable pieces with moves and peices values (add eval of h0 and h1 with stable pieces).
            NOTE: I THINK WE SHOULD LSO TRY THIS WITHOUT ADDING PIECES (lots of strat guides say pieces is bad indicator)
            """
            # get number of pieces value (h0)
            pieces_val = board.count_score(self.symbol) - board.count_score(self.oppSym)
            # get legal moves value (h1)
            player_legal_moves, opp_legal_moves = 0, 0
            for c in range(0, board.get_num_cols()):
                for r in range(0, board.get_num_rows()):
                    if board.is_legal_move(c, r, self.symbol) : player_legal_moves += 1 
                    if board.is_legal_move(c, r, self.oppSym) : opp_legal_moves += 1 
            moves_val = player_legal_moves - opp_legal_moves
            # get stable pieces value
            player_stable_pieces, opp_stable_pieces = 0, 0
            for c in range(0, board.get_num_cols()):
                for r in range(0, board.get_num_rows()):
                    symbol = board.get_cell(c, r)
                    if symbol == '.': # empty cell
                        continue
                    if symbol == self.symbol: # check if player piece is stable
                        # check if flankable in its col
                        flankable_above, flankable_below = False, False
                        for rows in range(0, r): # check rows less than r
                            if board.get_cell(c, rows) == '.' or board.get_cell(c, rows) == self.oppSym: flankable_above = True
                        for rows in range(r, board.get_num_rows()): # check rows greater than r
                            if board.get_cell(c, rows) == '.' or board.get_cell(c, rows) == self.oppSym: flankable_below = True
                        if flankable_above and flankable_below: continue # peice is not stable
                        # check if flankable in its row
                        flankable_left, flankable_right = False, False
                        for cols in range(0, c): # check rows less than r
                            if board.get_cell(cols, r) == '.' or board.get_cell(cols, r) == self.oppSym: flankable_left = True
                        for rows in range(r, board.get_num_rows()): # check rows greater than r
                            if board.get_cell(cols, r) == '.' or board.get_cell(cols, r) == self.oppSym: flankable_right = True
                        if flankable_left and flankable_right: continue # piece is not stable
                        # check if flankable by its negative slope diagonal
                        check_c,  check_r = c, r
                        flankable_NW = False
                        flankable_SE = False
                        while(board.get_cell(check_c - 1, check_r - 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells NW of cell
                            if board.get_cell(check_c - 1, check_r - 1) == '.' or board.get_cell(check_c - 1, check_r - 1) == self.oppSym: 
                                flankable_NW = True
                                break
                            check_c -= 1
                            check_r -= 1
                        check_c,  check_r = c, r
                        while(board.get_cell(check_c + 1, check_r + 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells SE of cell
                            if board.get_cell(check_c + 1, check_r + 1) == '.' or board.get_cell(check_c + 1, check_r + 1) == self.oppSym: 
                                flankable_SE = True
                                break
                            check_c += 1
                            check_r += 1
                        if flankable_NW and flankable_SE: continue # piece is not stable
                        # check if flankable by its positive slope diagonal
                        check_c,  check_r = c, r
                        flankable_NE = False
                        flankable_SW = False
                        while(board.get_cell(check_c + 1, check_r - 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells NW of cell
                            if board.get_cell(check_c + 1, check_r - 1) == '.' or board.get_cell(check_c + 1, check_r - 1) == self.oppSym: 
                                flankable_NE = True
                                break
                            check_c += 1
                            check_r -= 1
                        check_c,  check_r = c, r
                        while(board.get_cell(check_c - 1, check_r + 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells SE of cell
                            if board.get_cell(check_c - 1, check_r + 1) == '.' or board.get_cell(check_c - 1, check_r + 1) == self.oppSym: 
                                flankable_SW = True
                                break
                            check_c += 1
                            check_r += 1
                        if flankable_NE and flankable_SW: continue # piece is not stable

                        # Not flankable by row, column, or diagonal, so the piece is stable
                        player_stable_pieces += 1

                    elif symbol == self.oppSym: # check if opponent piece is stable
                        # check if flankable in its col
                        flankable_above, flankable_below = False, False
                        for rows in range(0, r): # check rows less than r
                            if board.get_cell(c, rows) == '.' or board.get_cell(c, rows) == self.symbol: flankable_above = True
                        for rows in range(r, board.get_num_rows()): # check rows greater than r
                            if board.get_cell(c, rows) == '.' or board.get_cell(c, rows) == self.symbol: flankable_below = True
                        if flankable_above and flankable_below: continue # peice is not stable
                        # check if flankable in its row
                        flankable_left, flankable_right = False, False
                        for cols in range(0, c): # check rows less than r
                            if board.get_cell(cols, r) == '.' or board.get_cell(cols, r) == self.symbol: flankable_left = True
                        for cols in range(r, board.get_num_rows()): # check rows greater than r
                            if board.get_cell(cols, r) == '.' or board.get_cell(cols, r) == self.symbol: flankable_right = True
                        if flankable_left and flankable_right: continue # peice is not stable
                         # check if flankable by its negative slope diagonal
                        check_c,  check_r = c, r
                        flankable_NW = False
                        flankable_SE = False
                        while(board.get_cell(check_c - 1, check_r - 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells NW of cell
                            if board.get_cell(check_c - 1, check_r - 1) == '.' or board.get_cell(check_c - 1, check_r - 1) == self.symbol: 
                                flankable_NW = True
                                break
                            check_c -= 1
                            check_r -= 1
                        check_c,  check_r = c, r
                        while(board.get_cell(check_c + 1, check_r + 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells SE of cell
                            if board.get_cell(check_c + 1, check_r + 1) == '.' or board.get_cell(check_c + 1, check_r + 1) == self.symbol: 
                                flankable_SE = True
                                break
                            check_c += 1
                            check_r += 1
                        if flankable_NW and flankable_SE: continue # piece is not stable
                        # check if flankable by its positive slope diagonal
                        check_c,  check_r = c, r
                        flankable_NE = False
                        flankable_SW = False
                        while(board.get_cell(check_c + 1, check_r - 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells NW of cell
                            if board.get_cell(check_c + 1, check_r - 1) == '.' or board.get_cell(check_c + 1, check_r - 1) == self.symbol: 
                                flankable_NE = True
                                break
                            check_c += 1
                            check_r -= 1
                        check_c,  check_r = c, r
                        while(board.get_cell(check_c - 1, check_r + 1)):  # NOTE: get_cell returns none if not in bounds
                            # check cells SE of cell
                            if board.get_cell(check_c - 1, check_r + 1) == '.' or board.get_cell(check_c - 1, check_r + 1) == self.symbol: 
                                flankable_SW = True
                                break
                            check_c += 1
                            check_r += 1
                        if flankable_NE and flankable_SW: continue # piece is not stable

                        # Not flankable by row, column or diagonal, so the piece is stable
                        opp_stable_pieces += 1
                          
            stable_val = player_stable_pieces - opp_stable_pieces
            print(stable_val) # TEMP PRINT STATEMENT
            value = pieces_val + moves_val + stable_val
        return value

    # TODO: Fix error where sometimes an invalid move is appended
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

       
        





