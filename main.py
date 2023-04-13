import pygame
import sys
import math
import numpy as np
import random

pygame.init()

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT),dtype=int)
    return board

def drop_piece(board,row,col,piece):
    board[row][col] = piece

def is_valid_location(board,col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board,col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board,0))

def winning_move(board,piece):
    #horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    
    #vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    
    #diagonal positive
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    
    #diagonal negative
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = 1
	if piece == 1:
		opp_piece = 2

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, 2):
				return (None, 100000000000000)
			elif winning_move(board, 1):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, 2))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, 2)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, 1)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board():
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen,BLUE,(c*SQUARESIZE,r*SQUARESIZE+SQUARESIZE,SQUARESIZE,SQUARESIZE))
            pygame.draw.circle(screen,BLACK,(int(c*SQUARESIZE+SQUARESIZE/2),int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)),RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen,RED,(int(c*SQUARESIZE+SQUARESIZE/2),screen_height-int(r*SQUARESIZE+SQUARESIZE/2)),RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen,YELLOW,(int(c*SQUARESIZE+SQUARESIZE/2),screen_height-int(r*SQUARESIZE+SQUARESIZE/2)),RADIUS)

    pygame.display.update()

COLUMN_COUNT = 7
ROW_COUNT = 6
SQUARESIZE = 100
EMPTY = 0
WINDOW_LENGTH = 4
screen_width = COLUMN_COUNT*SQUARESIZE
screen_height = (ROW_COUNT+1)*SQUARESIZE
RADIUS = int(SQUARESIZE/2 -5)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0,0,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)

font = pygame.font.Font(None, 75)
screen = pygame.display.set_mode((screen_width, screen_height))
board = create_board()

def screen1():
    start_text = font.render("START", True, WHITE)
    start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    screen2()
            elif event.type == pygame.MOUSEMOTION:
                if start_rect.collidepoint(event.pos):
                    start_text = font.render("START", True, RED)
                else:
                    start_text = font.render("START", True, WHITE)

        screen.fill(BLACK)
        screen.blit(start_text, start_rect)
        pygame.display.flip()

def screen2():
    vs_ai_text = font.render("1_VS_AI", True, WHITE)
    vs_ai_rect = vs_ai_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
    vs_player_text = font.render("1_VS_1", True, WHITE)
    vs_player_rect = vs_player_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100 ))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if vs_ai_rect.collidepoint(event.pos):
                    screen3()
                elif vs_player_rect.collidepoint(event.pos):
                    screen4(1)
            elif event.type == pygame.MOUSEMOTION:
                if vs_ai_rect.collidepoint(event.pos):
                    vs_ai_text = font.render("1_VS_AI", True, RED)
                else:
                    vs_ai_text = font.render("1_VS_AI", True, WHITE)
                if vs_player_rect.collidepoint(event.pos):
                    vs_player_text = font.render("1_VS_1", True, RED)
                else:
                    vs_player_text = font.render("1_VS_1", True, WHITE)

        screen.fill(BLACK)
        screen.blit(vs_ai_text, vs_ai_rect)
        screen.blit(vs_player_text, vs_player_rect)
        pygame.display.flip()

def screen3():
    easy_text = font.render("EASY", True, WHITE)
    easy_rect = easy_text.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
    medium_text = font.render("MEDIUM", True, WHITE)
    medium_rect = medium_text.get_rect(center=(screen_width // 2, screen_height // 2 ))
    hard_text = font.render("HARD", True, WHITE)
    hard_rect = hard_text.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    screen4(2,1)
                elif medium_rect.collidepoint(event.pos):
                    screen4(2,3)
                elif hard_rect.collidepoint(event.pos):
                    screen4(2,5)
            elif event.type == pygame.MOUSEMOTION:
                if easy_rect.collidepoint(event.pos):
                    easy_text = font.render("EASY", True, RED)
                else:
                    easy_text = font.render("EASY", True, WHITE)
                if medium_rect.collidepoint(event.pos):
                    medium_text = font.render("MEDIUM", True, RED)
                else:
                    medium_text = font.render("MEDIUM", True, WHITE)
                if hard_rect.collidepoint(event.pos):
                    hard_text = font.render("HARD", True, RED)
                else:
                    hard_text = font.render("HARD", True, WHITE)
        screen.fill(BLACK)
        screen.blit(easy_text, easy_rect)
        screen.blit(medium_text, medium_rect)
        screen.blit(hard_text, hard_rect)
        pygame.display.flip()    
        
def screen4(Player_or_Ai,difficluty=0):
    board.fill(0)
    screen.fill(BLACK)
    draw_board()
    if Player_or_Ai == 1:
        Player_Screen()
    else:
        Ai_Screen(difficluty)

def Player_Screen():
    turn = 0
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen,BLACK,(0,0,screen_width,SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen,RED,(posx,int(SQUARESIZE/2)),RADIUS)
                else:
                    pygame.draw.circle(screen,YELLOW,(posx,int(SQUARESIZE/2)),RADIUS)
            
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen,BLACK,(0,0,screen_width,SQUARESIZE))

                if turn == 0:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board,col):
                        row = get_next_open_row(board,col)
                        drop_piece(board,row,col,1)

                        if winning_move(board,1):
                            label = font.render('Player 1 Wins',1,RED)
                            screen.blit(label,(180,40))
                            game_over = True
                            

                else:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board,col):
                        row =get_next_open_row(board,col)
                        drop_piece(board,row,col,2)

                        if winning_move(board,2):
                            label = font.render('Player 2 Wins',1,YELLOW)
                            screen.blit(label,(180,40))
                            game_over = True
                            

                print_board(board)
                
                draw_board()

                turn += 1
                turn = turn % 2
                
                if game_over:
                    pygame.time.wait(10000)

def Ai_Screen(difficulty):
    PLAYER = 0
    AI = 1
    turn = random.randint(PLAYER,AI)
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen,BLACK,(0,0,screen_width,SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen,RED,(posx,int(SQUARESIZE/2)),RADIUS)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen,BLACK,(0,0,screen_width,SQUARESIZE))

                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board,col):
                        row = get_next_open_row(board,col)
                        drop_piece(board,row,col,1)

                        if winning_move(board,1):
                            label = font.render('YOU WIN',1,RED)
                            screen.blit(label,(230,40))
                            game_over = True
                        
                        turn += 1
                        turn = turn % 2

                        print_board(board)
                        draw_board()
        
        if turn == AI and not game_over:

            col, minimax_score = minimax(board, difficulty, -math.inf, math.inf, True)

            if is_valid_location(board,col):
                pygame.time.wait(500)
                row =get_next_open_row(board,col)
                drop_piece(board,row,col,2)

                if winning_move(board,2):
                    label = font.render('YOU LOOOSE',1,YELLOW)
                    screen.blit(label,(180,40))
                    game_over = True
                            

                print_board(board)
                draw_board()

                turn += 1
                turn = turn % 2
        
        if game_over:
            pygame.time.wait(3000)

screen1()



