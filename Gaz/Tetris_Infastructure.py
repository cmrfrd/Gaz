#
#This file contains the infastructure for tetris repurposed for Gaz
#

tetris_shapes = [
        [[1, 1, 1],
         [0, 1, 0]],

        [[0, 2, 2],
         [2, 2, 0]],

        [[3, 3, 0],
         [0, 3, 3]],

        [[4, 0, 0],
         [4, 4, 4]],

        [[0, 0, 5],
         [5, 5, 5]],

        [[6, 6, 6, 6]],

        [[7, 7],
         [7, 7]]
]

cols = 10
rows = 22

rotations_by_index = {#number of rotations by index of piece in tetris shapes
	6:1,
	1:2,2:5,5:2,
	0:4,3:4,4:4
}

def rotate_clockwise(shape):
    '''rotates the shape clockwise around [0][0]
    '''
    return [ [ shape[y][x]
               for y in xrange(len(shape)) ]
             for x in xrange(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
    '''makes sure a board doesn't collide with a piece, returns bool
    '''
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def join_matrixes(mat1, mat2, mat2_off):
    '''combines 2 boards and an offset
    '''
        off_x, off_y = mat2_off
        for cy, row in enumerate(mat2):
                for cx, val in enumerate(row):
                        mat1[cy+off_y-1 ][cx+off_x] += val
        return mat1

def get_piece_index(shape):
    '''
    Since tetris piece variables are morphed in place, 
    we need to keep rotating them to get their index
    '''
    rotations = 0
    index = -1
    for r in range(3):
        try:
            index = tetris_shapes.index(shape)
        except ValueError:
            shape = rotate_clockwise(shape)
    return index

def get_rotations(shape):
    rotations = 0
    rotations = rotations_by_index[get_piece_index(shape)]
            
    rotated_shape = shape
    for r in range(rotations):
        rotated_shape = rotate_clockwise(rotated_shape)
        yield rotated_shape

class Row(list):
    '''Just a list object that will be expanded upon
    '''
    def __init__(self, row):
        list.__init__(self, row)
        self.is_full = all(row)

class Column(list):
    '''Column object is just a list with some analytic structure ontop
    '''
    def __init__(self, col_list):
        list.__init__(self, col_list)
        self.height_gap = False
        self.height = False
        self.spaces = False

	def __eq__(self, other_col_list):
            return self == other_col_list

	def remove_space(self, index):
            '''delete index and add 0 at end. represents the 'clearing' of a line
            '''
            if index in range(len(self)):
                del self[index]
                return [0] + self
            return self

	def calc_data(self, update=False):
            '''calculates 3 pieces of data about a column
            '''
            if not self.height_gap or update:
                self.calc_height_gap()
		if not self.height or update:
                    self.height = len(self) - self.height_gap
		if not self.spaces or update:
                    self.spaces = self.count(0) - self.height_gap
		return self

	def calc_height_gap(self):
            '''gets the gap between the height and max ceiling
            '''
            for i,j in enumerate(self):
                if j != 0:
                    self.height_gap = i
                    break

class Board(list):
    '''
    Board object contains columns 

    provides more advanced analysis by providing more data.
    Also allows you to "fake add" piece and iterate through slices of the board
    '''

    def __init__(self, board_list):
        if isinstance(board_list, Board):
            self = board_list
        else:
            list.__init__(self, [Column(col).calc_data() for col in board_list])

            self.max = False
            self.min = False
            self.average = False
            self.mode = False
            self.total_spaces = False
            self.full_rows = False
            self.row_completeness = False

    def invert(self):
        '''return just a new list in "row" format
        '''        
        return [list(row) for row in zip(*self)]
	
    def calc_data(self, update=False):		

        #to save calc time. calculate full rows and row completeness in one pass
        #also removes complete rows
        if not self.full_rows or self.row_completeness or update:

            #by default there will always be one complete row
            self.full_rows = 1
            self.row_completeness = 1
            row_board = self.invert()					

            if len(row_board[0]) == cols:					    

                #find the completeness of each row by getting %
                for index, row in enumerate(row_board[:-1:-1]):			
                    perc_complete = float(len(row) - row.count(0)) / len(row)       
                    row_complete = perc_complete / (index + 1)                      
                    self.row_completeness += row_complete
                    
                #if the row is complete remove it
                for index, row in enumerate(row_board[:-1:-1]):
                    if all(row):						
                        for col in self:col.remove_space(index)			
                        self.full_rows += 1 					

                        self.row_completeness /= rows

        #general stats about the baord
        if not self.max or update:
            self.max = max(col.height for col in self)
        if not self.min or update:
            self.min = min(col.height for col in self)
        if not self.average or update:
            self.average = sum(col.height for col in self)/len(self)
        if not self.mode or update:
            heights = [col.height for col in self]
            self.mode = max(heights, key=heights.count)
        if not self.total_spaces or update:
            self.total_spaces = sum(col.spaces for col in self)
        return self

    def data(self):
        '''print the data to console
        '''
        print "Max: %d" % (self.max)
        print "Avg: %f" % (self.average)
        print "Mode: %d" % (self.mode)
        print "Spaces: %d" % (self.total_spaces)
        print "Rows: %d" % (self.full_rows)
        print "Comp: %f" % (self.row_completeness)

    def calc_col_data(self):
        for col in self:
            col.calc_data(True)

    def slice_iter(self, width):
        '''iterator that returns a "board" object
        '''
        assert 1 <= width <= len(self), "Width not within bounds of board"
        
        for col in range(0, len(self) - width + 1):
            yield (col, Board(self[col:col+width][:]))
            
    def fake_add(self, x, piece):
        '''returns board object with piece "insta_dropped" at an x 
        '''
        row_board = self.invert()	
            
        assert x in [0]+range(len(self) - len(zip(*piece)) + 1), "X not within bounds"
        
        #start from top down, once there is a collision, add and return new board
        for y in range(1, len(row_board)):			
            if check_collision(row_board, piece, (x, y)):	
                row_board_with_piece = join_matrixes(row_board, piece, (x, y))	
                return Board(zip(*row_board_with_piece))			
