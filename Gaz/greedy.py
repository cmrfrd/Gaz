from Tetris_Infastructure import get_rotations

#a bunch of scorign functions I tried...
#in order are the ones that worked best

def score(board):
    
    numer = (float(board.full_rows))
    denom = (board.max + board.min + board.average + board.mode + board.total_spaces + 1)

    return numer / denom

def score_2(board):
    return board.row_completeness

def bad_score(board):
    return board.full_rows * e**-(board.total_spaces + board.max + board.min + board.average + board.mode)

def bad_score_2(board):
    return ((board.max / (board.average + board.mode + board.total_spaces)) / board.min)

def bad_score_3(board):
    return float(board.full_rows) ** -(board.max + board.min + board.average + board.mode + board.total_spaces + 1)

def bad_score_4(board):
    return (board.max + board.min + board.average + board.mode + board.total_spaces + 1) % board.full_rows

def bad_score_5(board):
    return (float(board.min)/board.max) * (board.full_rows/(board.total_spaces+1))

def bad_score_6(board):
    return (board.min/float(board.max)) * (board.mode/board.average) * (board.full_rows/(float(board.total_spaces)+1))

class greedy(object):
    '''greedy implements a greedy algorithm
    '''
    def __init__(self, time_const=0.5):
        self.score_func = score
        self.time_const = time_const

    def get_next_move(self, board, piece):
        scores = {}

        for rotation_index, rotated_piece in enumerate(get_rotations(piece)):
            for slice_index, slice in board.slice_iter(len(zip(*rotated_piece))):

                #calc data for each board
                slice_without_piece = slice.calc_data()
                board_without_piece = board.calc_data()	

                #add the piece to the board
                slice_with_piece = slice.fake_add(0, rotated_piece).calc_data()
                board_with_piece = board.fake_add(slice_index, rotated_piece).calc_data()			
                
                #calculate the score
                total_score = self.score_func(slice_with_piece) + \
                              self.score_func(board_with_piece)
            
        scores[total_score] = (slice_index, rotated_piece)
    
        best_move = scores[max(scores.keys())]
        sleep(self.time)
    
        return best_move

