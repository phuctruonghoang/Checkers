'''
Delete comment and compile.
Goodluck
'''
from copy import deepcopy
import pygame #import packet pygame
from pygame.locals import * #import values và constants
from sys import exit #import exit function

turn = 'white' # Biến turn lưu lượt đánh của người chơi là màu trắng
selectPosition = (0, 0) #Tuple lưu giá trị tọa độ x,y khi người chơi chọn trên bàn cờ
board = 0 #Khởi tạo đối tượng board (bàn cờ)
moveLimit = 150 #Tổng số lượt đi của hai bên là 150
countMove = 0 #Biến đếm số lượt đi của người chơi và agent

best_move = () #Chứa giá trị tọa độ x, y tốt nhất để agent di chuyển được xác định bằng thuật toán alpha_beta
black  = () #Khởi tạo đối tượng black player
white = () #khởi tạo đối tượng white player

screenWidth = 512
screenHeight = 512
board_size = 8 
fps = 5 


#class biểu diễn các quân cờ trên bàn cờ
class Piece(object):
    def __init__(self, color, king):
        self.color = color #black hoặc white
        self.king = king #True hoặc False

#class biểu diễn player
class Player(object):
    def __init__(self, type, color, playerDeep):
        self.type = type #agent hoặc human
        self.color = color #black hoặc white
        self.playerDeep = playerDeep #Độ sâu của thuật toán 


def initBoard(): #thiết lập bàn cờ với tất cả các quân cờ
    global  countMove
    countMove = 0 #reset lại biến đếm lượt đi của hai bên khi khởi tạo bàn cờ mới

    result = [
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, -1, 0, -1, 0, -1, 0],
    [0, -1, 0, -1, 0, -1, 0, -1],
    [-1, 0, -1, 0, -1, 0, -1, 0]
    ] #Thiết lập bàn cờ ban đầu
    for m in range(8): 
        for n in range(8):
            if (result[m][n] == 1):
                result[m][n] = Piece('black', False) #quân cờ đen không phải là vua
            elif (result[m][n] == -1):
                result[m][n] = Piece('white', False) #quân cờ trắng không phải là vua
    return result

def anyMove(board, player): #trả về array với tất cả các vị trí di chuyển có sẵn cho người chơi trên bàn cờ
    moves = [] #lưu các vị trí có thể di chuyển hoặc nhảy

    for m in range(8):
        for n in range(8):
            if board[m][n] != 0 and board[m][n].color == player: #kiểm tra tất cả các quân cờ của human hoặc agent
                if possibleJump([m, n], [m + 1, n + 1], [m + 2, n + 2], board) == True:  
                    moves.append([m, n, m + 2, n + 2])
                if possibleJump([m, n], [m-1, n + 1], [m-2, n + 2], board) == True: 
                    moves.append([m, n, m-2, n + 2])
                if possibleJump([m, n], [m + 1, n-1], [m + 2, n-2], board) == True: 
                    moves.append([m, n, m + 2, n-2])
                if possibleJump([m, n], [m-1, n-1], [m-2, n-2], board) == True: 
                    moves.append([m, n, m-2, n-2])

    if len(moves) == 0: #nếu không có vị trí nào có thể nhảy trong list
		#kiểm tra các nước di chuyển bình thường
        for m in range(8):
            for n in range(8):
                if board[m][n] != 0 and board[m][n].color == player: 
                    if possibleMove([m, n], [m + 1, n + 1], board) == True: 
                        moves.append([m, n, m + 1, n + 1])
                    if possibleMove([m, n], [m-1, n + 1], board) == True: 
                        moves.append([m, n, m-1, n + 1])
                    if possibleMove([m, n], [m + 1, n-1], board) == True: 
                        moves.append([m, n, m + 1, n-1])
                    if possibleMove([m, n], [m-1, n-1], board) == True: 
                        moves.append([m, n, m-1, n-1])

    return moves #trả về list các vị trí có thể nhảy hoặc di chuyển 


def possibleJump(before, middle, after, board): #trả về true nếu nước nhảy hợp lệ
    if after[0] < 0 or after[0] > 7 or after[1] < 0 or after[1] > 7: #kiểm tra xem có nhảy ra khỏi biên bàn cờ hay không
        return False
    if board[after[0]][after[1]] != 0: #kiểm tra đích nhảy đến có trống hay không 
        return False
    if board[middle[0]][middle[1]] == 0: #kiểm tra quân cờ nằm ở giữa vị trí ban đầu và đích có trống hay không, nếu trống không nhảy được
        return False
    if board[before[0]][before[1]].color == 'white':
        if board[before[0]][before[1]].king == False and after[0] > before[0]: #chỉ được di chuyển tới mà không được lui
            return False 
        if board[middle[0]][middle[1]].color != 'black': #chỉ được nhảy qua quân cờ đen
            return False 
        return True 
    
    if board[before[0]][before[1]].color == 'black':
        if board[before[0]][before[1]].king == False and after[0] < before[0]: #chỉ được di chuyển tới mà không được lui
            return False 
        if board[middle[0]][middle[1]].color != 'white': #chỉ được nhảy qua quân cờ trắng
            return False 
        return True 

def possibleMove(before, after, board): #trả về true nếu bước đi hợp lệ
    if after[0] < 0 or after[0] > 7 or after[1] < 0 or after[1] > 7: #kiểm tra xem có di chuyển ra khỏi biên bàn cờ hay không
        return False
    if board[after[0]][after[1]] != 0: #kiểm tra đích di chuyển đến có trống hay không 
        return False
    if board[ before[0]][ before[1]].king == False and board[ before[0]][ before[1]].color == 'white': #đối với các quân cờ trắng không phải là vua
        if after[0] >=  before[0]: 
            return False #chỉ được di chuyển tới không lui
        return True 
    if board[ before[0]][ before[1]].king == False and board[ before[0]][ before[1]].color == 'black': #đối với các quân cờ đen không phải là vua
        if after[0] <=  before[0]: #chỉ được di chuyển tới không lui
            return False 
        return True 
    if board[ before[0]][ before[1]].king == True: #nếu là vua được di chuyển tới và lui
        return True 
    
    return True
        
def makeMove(a, b, board): #thực hiện di chuyển từ vị trí ban đầu đến đích
    board[b[0]][b[1]] = board[a[0]][a[1]] #thực hiện di chuyển
    board[a[0]][a[1]] = 0 #xóa quân cờ ở vị trí đầu 
    
    #kiểm tra quân cờ có được phong vương hay không
    if b[0] == 0 and board[b[0]][b[1]].color == 'white': 
        board[b[0]][b[1]].king = True
    if b[0] == 7 and board[b[0]][b[1]].color == 'black': 
        board[b[0]][b[1]].king = True
    
    if abs(a[0] - b[0]) == 2: #nếu quân cờ thực hiện nhảy 
        board[(a[0] + b[0]) / 2][(a[1] + b[1]) / 2] = 0 #xóa quân cờ ở giữa vị trí ban đầu và đích 


def scorePeice(board, color): #trả về điểm của mỗi quân cờ, nếu là vua điểm là 175, quân cờ thường là 100
    black = 0
    white = 0 
    for m in range(8):
        for n in range(8):
            if (board[m][n] != 0 and board[m][n].color == 'black'): #chọn quân cờ đen trên bàn cờ
                if board[m][n].king == False: 
                    black = black + 100 #100 điểm cho quân cờ thường 
                else: 
                    black = black + 175 #175 cho quân vua 
            elif (board[m][n] != 0 and board[m][n].color == 'white'): #chọn quân cờ trắng trên bàn cờ
                if board[m][n].king == False: 
                    white = white + 100 #100 điểm cho quân cờ thường
                else: 
                    white = white + 175 #175 cho quân vua 
    if color == 'white': 
        return white-black
    else: 
        return black-white

def scoreMove(board, color): #cộng thêm điểm cho các quân cờ khi di chuyển qua hướng đối phương
    black = 0
    white = 0 
    for m in range(8):
        for n in range(8):
            if (board[m][n] != 0 and board[m][n].color == 'black'): #chọn các quân cờ đen trên bàn cờ
                if board[m][n].king == False: #quân cờ thường 
                    black = black + (m * m)
            elif (board[m][n] != 0 and board[m][n].color == 'white'): #chọn các quân cờ trắng trên bàn cờ
                if board[m][n].king == False: #quân cờ thường 
                    white = white + ((7-m) * (7-m))
    if color == 'white': 
        return white-black
    else: 
        return black-white

def scoreKingMove(board, color): #quân vua khi di chuyển vào vị trí góc thì bị trừ điểm 
    black = 0
    white = 0  
    for m in range(8):
        if (board[m][0] != 0 and board[m][0].king == True):
            if board[m][0].color == 'black': 
                black = black - 25 #quân đen bị trì 25
            else: 
                white = white - 25 #quân trắng bị trì 25
        if (board[m][7] != 0 and board[m][7].king == True):
            if board[m][7].color == 'black': 
                black = black - 25 #quân đen bị trì 25
            else: 
                white = white - 25 #quân trắng bị trì 25
    if color == 'white': 
        return white-black
    else: 
        return black-white
    
def evaluate(board, color):
    return (scorePeice(board, color) + scoreMove(board, color) + scoreKingMove(board, color)) * 1 #Trả về tổng score của human hoặc agent


def endGame(board): #kiểm tra xem một bên còn cờ hay không 
    black, white = 0, 0 
    for m in range(8):
        for n in range(8):
            if board[m][n] != 0:
                if board[m][n].color == 'black': 
                    black = black + 1 #tổng số quân cờ đen 
                else: 
                    white = white + 1 #tổng số quân cờ trắng 

    return black, white


def alpha_beta(player, board, deep, alpha, beta):
    global best_move

    playerDeep = 0
    playerDeep = black.playerDeep #độ sâu gán cho agent

    end = endGame(board)

    if deep >= playerDeep or end[0] == 0 or end[1] == 0: #kiểm tra phải là node lá hay không 
        score = evaluate(board, player) # trả lại điểm đánh giá khi đến lá hoặc đến độ sâu cuối cùng của trạng thái bàn cờ
        return score

	#children = tất cả các nước cờ có thể đi cho người chơi 	
    moves = anyMove(board, player) #lấy tất các vị trí có thể di chuyển 

    if player == turn:
        for i in range(len(moves)): #lấy các node con 
            newBoard = deepcopy(board) #coppy bàn cờ hiện tại sang một bàn cờ tạm thời 
            makeMove((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), newBoard) #thực hiện di chuyển trong bàn cờ mới  
            if player == 'black': #chuyển đổi người chơi cho thuật toán 
                player = 'white'
            else: 
                player = 'black'

            score = alpha_beta(player, newBoard, deep + 1, alpha, beta)

            if score > alpha: # nếu score > alpha thì alpha = score; tìm được nước đi tốt nhất
                if deep == 0: 
                    best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]) 
                alpha = score
            if alpha >= beta: #nếu alpha >beta cắt tỉa nhánh 
                return alpha

        return alpha

    else:
        for i in range(len(moves)): #đối với mỗi node con 
            newBoard = deepcopy(board)
            makeMove((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), newBoard)

            if player == 'black': 
                player = 'white'
            else: 
                player = 'black'
			
			#  score = alpha-beta(other player,child,alpha,beta)
            score = alpha_beta(player, newBoard, deep + 1, alpha, beta)
			
			#nếu score < beta thì score = beta; đối thủ tìm được nước đi tốt nhất 
            if score < beta: 
                beta = score
            if alpha >= beta:  #nếu alpha > beta thì cắt tỉa 
                return beta
            
        return beta


def endTurn():
    global turn #sử dụng biến global 

    if turn == 'black':	
        turn = 'white'
    elif turn == 'white':	
        turn = 'black'


def agentPlay(player): # agent chơi cờ 
    global board, countMove 
    alpha = alpha_beta(player.color, board, 0, -10000, + 10000) # tìm best move 
   
    if alpha == -10000: #không còn nước đi 
        if player.color == white: 
            showWinner('black')
        else: 
            showWinner('white')

    makeMove(best_move[0], best_move[1], board) #thực hiện di chuyển sang vị trí mới 

    countMove = countMove + 1 #tăng biến đếm lượt đi 

    endTurn() #kết thúc lượt đi, đổi phiên đánh cờ cho đối thủ 
    
def initGame():
    global black, white 
    black = Player('agent', 'black',5) #khởi tạo agent chơi cờ màu đen với độ sâu thuật toán 5
    white = Player('human', 'white',0) #khởi tạo human chơi cờ màu trắng 
    board = initBoard()

    return board
		

def checkAnyMove(board, color): #kiểm tra xem còn nước đi hợp lệ nào không  
    result = anyMove(board, color)
    if len(result) == 0: #không còn nước đi 
        return False
    return True

def drawPiece(row, column, color, king): #vẽ các quân cờ trên bàn cờ 
    x = ((screenWidth / 8) * column) - (screenWidth / 8) / 2
    y = ((screenHeight / 8) * row) - (screenHeight / 8) / 2
	
    #thiết lập màu cho quân cờ 
    if color == 'black':
        border = (255, 255, 255)
        inside = (0, 0, 0)
    elif color == 'white':
        border = (0, 0, 0)
        inside = (255, 255, 255)
	
    pygame.draw.circle(screen, border, (int(x), int(y)), 24) 
    pygame.draw.circle(screen, inside, (int(x), int(y)), 20) 
	
   
    if king == True: #vẽ các quân cờ là vua 
        pygame.draw.circle(screen, border, (x + 6, y-6), 24) 
        pygame.draw.circle(screen, inside, (x + 6, y-6), 20) 


def showMessage(message): #hiện thông báo trên màn hình 
    text = font.render(' ' + message + ' ', True, (255, 255, 255), (120, 195, 46)) #tạo message
    textRect = text.get_rect() #tạo hình chữ nhật 
    textRect.centerx = screen.get_rect().centerx #thiết lập hình chữ nhật ở vị trí trung tâm 
    textRect.centery = screen.get_rect().centery
    screen.blit(text, textRect) 


def showWinner(winner): #hiển thị thông báo người chơi chiến thắng 
    global board
    
    if winner == 'draw': #hiển thị hòa và kết thúc game 
        showMessage('DRAW')
        pygame.display.flip()
        pygame.time.wait(2500)
        exit()
    elif winner == 'black': #hiển thị đen thắng và kết thúc game
        showMessage('BLACK WINS')
        pygame.display.flip()
        pygame.time.wait(2500)
        exit()
    elif winner == 'white': #hiển thị trắng thắng và kết thúc game
        showMessage('WHITE WINS')
        pygame.display.flip()
        pygame.time.wait(2500)
        exit()
        
    
def click(position): #hiển thị các ô vuông được chọn 
    global selectPosition, countMove 

    if(turn != 'black' and white.type != 'agent'):
        column = position[0] / (screenWidth / 8)
        row = position[1] / (screenHeight / 8)

        if board[int(row)][int(column)] != 0 and board[int(row)][int(column)].color == turn:
            selectPosition = row, column #cập nhật tọa độ x,y cho biết global selectPosition
        else:
            moves = anyMove(board, turn) #lấy tất cả các vị trí có thể đi cho player
            for i in range(len(moves)):
                if selectPosition[0] == moves[i][0] and selectPosition[1] == moves[i][1]:
                    if row == moves[i][2] and column == moves[i][3]:
                        makeMove(selectPosition, (row, column), board) #thực hiện di chuyển 
                        countMove = countMove + 1 #tăng biến đếm lượt đi 
                        endTurn() #kết thúc lượt đi và đổi phiên đánh cờ 

if __name__ == "__main__":
    pygame.init() #init pygame 
    board = initGame()
    screen = pygame.display.set_mode([screenWidth, screenHeight]) #thiết lập kích thước window 
    pygame.display.set_caption('Game Checkers') #thiết lập tiêu đề cho window
    clock = pygame.time.Clock() #tạo clock để game không refresh thường xuyên 

    background = pygame.image.load('background.png').convert() #load background
    font = pygame.font.Font('freesansbold.ttf', 24)  #font cho message

    while True: #main loop
        for event in pygame.event.get(): #event loop 
            if event.type == QUIT:
                exit() #thoát game 
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click(pygame.mouse.get_pos()) #mouse click 

        screen.blit(background, (0, 0)) #
        
		#hiển lượt đánh của player 
        if (turn != 'black' and white.type == 'human'): 
            showMessage('HUMAN PLAY')
		else:
            showMessage('AGENT PLAY')
        
		#vẽ các quân cờ trên bàn cờ 
        for m in range(8):
            for n in range(8):
                if board[m][n] != 0:
                    drawPiece(m + 1, n + 1, board[m][n].color, board[m][n].king)
        
		#kiểm tra trạng thái kết thúc game 
        if checkAnyMove(board, 'black') == False:
            showWinner('white')
        elif checkAnyMove(board, 'white') == False:
            showWinner('black')
        
        end = endGame(board)
        if end[1] == 0:	
            showWinner('black')
        elif end[0] == 0: 
            showWinner('white')
		
		#kiểm tra trạng thái hòa 
        elif countMove == moveLimit: 
            showWinner('draw')

        else: 
            pygame.display.flip() 
        
		#cpu play 
        if turn != 'white' and black.type == 'agent':
            agentPlay(black) 

        clock.tick(fps)
		
