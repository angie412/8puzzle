import time, random, copy, heapq
import pygame, sys
from pygame.locals import *

INFINITY = 1000000 
UP = (0, -1)
DOWN = (0, 1) 
LEFT = (-1, 0) 
RIGHT = (1, 0)

class Solutions(object):
    def __init__(self, size, board):
        self.size = size
        self.blank = None
        self.set_game(size, board) 
        self.sol_board = self.get_sol_board(size)
    
    def set_game(self, size, board): 
        self.board = self.get_board(board) 
        self.last_move = None 
        self.move_list = []
        self.is_solved = False 
        self.get_blank_coord(self.board) 
        self.count = 0
        self.node_id = 0

    def get_solution(self, type): 
        if type == 'DFS':
            return self.dfs()
        if type == 'IDA_STAR':
            return self.ida_star() 
        elif type == 'BFS':
            return self.bfs() 
        elif type == 'A_STAR': 
            return self.a_star()
        
    def ida_star(self): 
        g= 0
        h = get_heuristic(len(self.board[0]), self.board) 
        depth = g + h
        total_count = 0
        start = time.time()
        while True:
            self.last_move = None
            self.count = -1
            depth, count = self.dfs(0, depth)
            end = time.time()
            total_count += count
            print('depth =', h, 'count = %8s, total_count = %10s, time = %.2f'
                %(str(count), str(total_count), abs(end - start)))

            if self.is_solved:
                print('total_count = %s, depth = %d, len = %d, time = %.2f sec'
                        %(str(total_count), depth, len(self.move_list), abs(end - start))) 
                self.move_list.reverse()
                print(self.move_list)
                return self.move_list 
            h = depth
    def dfs(self, depth, max_depth): 
        self.count += 1
        h = get_heuristic(self.size, self.board) 
        f = depth + h
        if f > max_depth: 
            return f, self.count
        # if self.board == self.sol_board: 
        if h == 0:
            self.is_solved = True 
            return f, self.count
        
        x, y = self.blank
        moves = self.get_valid_move(x, y) 
        min = INFINITY
        for i in range(len(moves)):
            check_for_quit()

            move = random.choice(moves)
            moves.remove(move)
            self.move(x, y, move[0], move[1], self.board)
            self.last_move = (move[0] * -1, move[1] * -1)
            f, self.count = self.dfs(depth + 1, max_depth)
            self.move(x + move[0], y + move[1], move[0] * -1, move[1] * -1, self.board) 
            if f < min:
                min = f
            if self.is_solved:
                self.move_list.append(move) 
                return min, self.count
        return min, self.count
    
    def a_star(self):
        start = time.time()
        move_list = self.bfs()
        end = time.time()
        print('time = %.2f' % abs(end - start)) 
        print(move_list)
        return move_list
    
    def bfs(self):
        start = time.time() 
        show_info = 10 
        g= 0
        h = get_heuristic(len(self.board[0]), self.board) 
        f=g+h
        print('h =', h)
        parent = 0
        board = self.board[:]
        move = None
        node = Node(board, self.blank, move, self.node_id, parent, f, g) 
        close = []
        open = []
        self.expand_node(open, node)
        while open:
            check_for_quit()
            node = heapq.heappop(open)
            if self.node_id >= show_info or node.f == node.g:
                print("f = %d, g = %2d, node count = %8d, time = %6.2f" %(node.f, node.g, self.node_id, abs(time.time() - start)))
            if show_info < 100000: show_info *= 10
            else: show_info += 500000
        # if node.board == self.sol_board: 
        if node.f == node.g:
            print('open list = %d, closed list = %d, node_No = %d' % (len(open), len(close), self.node_id))
            # open.clear()
            return self.make_path(close, node.info) 
        close.append(node.info) 
        self.expand_node(open, node)

        return None
    
    def make_path(self, info_list, inf): 
        moves = [inf['move']]
        while info_list:
            info = info_list.pop()
            if info['id'] == inf['parent']:
                moves.append(info['move'])
                inf = info 
        moves.reverse()
        print('shortest path length= %d' %(len(moves))) 
        return moves
    
    def expand_node(self, queue, nodes): # g(depth) 정보 필요 
        x, y = nodes.blank
        if nodes.info['move']:
            dx, dy = nodes.info['move']
            self.last_move = (dx * -1, dy * -1) 
        moves = self.get_valid_move(x, y)
        
        for move in moves:
            board = []
            dx, dy = move
            board = copy.deepcopy(nodes.board) 
            self.move(x, y, dx, dy, board)
            blank = self.blank
            self.node_id += 1

            id = self.node_id
            parent = nodes.info['id']
            h = get_heuristic(len(board[0]), board)
            g = nodes.g + 1
            node = Node(board, blank, move, id, parent, g + h, g)
            heapq.heappush(queue, node)
            # heapq 사용법 아래 사이트 참고
            # https://stackoverflow.com/questions/47912064/typeerror-not-supported- between-instances-of-heapnode-and-heapnode
    
    def get_board(self, grid): 
        b = []
        for boards in grid: 
            row = []
            for tile in boards: 
                row.append(tile.id)
            b.append(row) 
        return b
    
    def get_sol_board(self, size): 
        b = []
        for y in range(size): 
            row = []
            for x in range(size): 
                row.append(x + y * size + 1)
            b.append(row)

        b[size - 1][size - 1] = 0 
        return b
        
    def get_blank_coord(self, board): 
        for y in range(len(board)):
            for x in range(len(board[0])): 
                if board[y][x] == 0:
                    self.blank = (x, y) 
                    return
    def is_tile(self, x, y, move): 
        x += move[0]
        y += move[1]
        return ((x >= 0 and x < self.size) and (y >= 0 and y < self.size))
    
    def get_valid_move(self, x, y):
        moves = [UP, DOWN, LEFT, RIGHT] 
        if self.last_move:
            moves.remove(self.last_move) 
        for i in range(len(moves) - 1, -1, -1):
            if not self.is_tile(x, y, moves[i]): 
                moves.remove(moves[i])
        return moves
    
    def move(self, x, y, dx, dy, board): 
        board[y][x] = board[y + dy][x + dx]
        board[y + dy][x + dx] = 0 
        self.blank = (x + dx, y + dy)
        
    def print_board(self, board): 
        for grid in board:
            for tile in grid: 
                print(tile, end=' ')
            print() 
        print()
        
class Node(object):
    def __init__(self, board, blank, move, id, parent, f, g):
        self.board = board 
        self.blank = blank 
        self.f = f
        self.g = g
        self.info = {'id': id, 'parent': parent, 'move': move}
    
    def __lt__(self, other): 
        return self.f < other.f
    
    def __eq__(self, other): 
        if not other:
            return False
        if not isinstance(other, Node):

            return False 
        return self.f == other.f
    
def get_heuristic(size, board):
    md_3 = [[0, 0, 0, 0, 0, 0, 0, 0, 0], # 0
            [0, 1, 2, 1, 2, 3, 2, 3, 4], # 1 
            [1, 0, 1, 2, 1, 2, 3, 2, 3], # 2 
            [2, 1, 0, 3, 2, 1, 4, 3, 2], # 3 
            [1, 2, 3, 0, 1, 2, 1, 2, 3], # 4 
            [2, 1, 2, 1, 0, 1, 2, 1, 2], # 5 
            [3, 2, 1, 2, 1, 0, 3, 2, 1], # 6 
            [2, 3, 4, 1, 2, 3, 0, 1, 2], # 7 
            [3, 2, 3, 2, 1, 2, 1, 0, 1]] # 8
    
    md_4 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0 
            [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6], # 1 
            [1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4, 4, 3, 4, 5], # 2 
            [2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3, 5, 4, 3, 4], # 3 
            [3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2, 6, 5, 4, 3], # 4 
            [1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5], # 5 
            [2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4], # 6 
            [3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3], # 7 
            [4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2], # 8 
            [2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4], # 9 
            [3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3], # 10
            [4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2], # 11 
            [5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1], # 12 
            [3, 4, 5, 6, 2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3], # 13 
            [4, 3, 4, 5, 3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2], # 14 
            [5, 4, 3, 4, 4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1]] # 15
    md = 0
    for y in range(size):
        for x in range(size): 
            if size == 3:
                md += md_3[board[y][x]][x + y * size] 
            else:
                md += md_4[board[y][x]][x + y * size]
    
    x=1
    for i in range(size):
        row = []
        for j in range(size):
            row.append(board[i][ j])
        for y in range(len(row) - 1, - 1, -1):
            if row[y] > size * x or row[y] == 0 or row[y] <= size * (x - 1): 
                row.remove(row[y])
            x += 1
            md = get_manhattan_distance(row, md)

    x=1
 
    for i in range(size): 
        row = []
        for j in range(size): 
            row.append(board[ j][i])
        for y in range(len(row) - 1, -1, -1):
            if row[y] == x or row[y] == x + size or row[y] == x + size * 2 or row[y] == x +size * 3:
                continue
            else : 
                row.remove(row[y])
        x += 1
        md = get_manhattan_distance(row, md) 
    return md

def get_manhattan_distance(row, md): 
    nums = len(row)
    if nums > 1:
        if nums == 2:
            if row[0] > row[1]: 
                md += 2
        elif nums == 3:
            if row[0] > row[1] or row[0] > row[2]:
                md += 2
            if row[1] > row[2]: 
                md += 2
            if row[0] > row[1] and row[0] > row[2]:
                md += 2
        elif nums == 4:
            if row[0] > row[1] or row[0] > row[2] or row[0] > row[3]:
                md += 2
            if row[1] > row[2] or row[1] > row[3]:
                md += 2
            if row[2] > row[3]: 
                md += 2
            if row[1] > row[2] and row[1] > row[3]: 
                md += 2
            if row[0] > row[1] and row[0] > row[2] and row[0] > row[3]: 
                md += 2
    return md


def terminate(): 
    pygame.quit()
    sys.exit()

def check_for_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back