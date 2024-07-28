import os
import pygame
import chess

# Constants
WIDTH, HEIGHT = 512, 512  # Chessboard dimensions
DIMENSION = 8  # Chessboard is 8x8
SQ_SIZE = WIDTH // DIMENSION  # Size of each square
IMAGES = {}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

# Load images
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    images_path = os.path.join(os.getcwd(), 'wooden_images')
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(os.path.join(images_path, f"{piece}.png")), (SQ_SIZE, SQ_SIZE))

# Load sounds
def load_sounds():
    sounds_path = os.path.join(os.getcwd(), 'sounds')
    move_sound = pygame.mixer.Sound(os.path.join(sounds_path, 'move.mp3'))
    capture_sound = pygame.mixer.Sound(os.path.join(sounds_path, 'capture.mp3'))
    check_sound = pygame.mixer.Sound(os.path.join(sounds_path, 'check.mp3'))
    checkmate_sound = pygame.mixer.Sound(os.path.join(sounds_path, 'checkmate.mp3'))
    castle_sound = pygame.mixer.Sound(os.path.join(sounds_path, 'castle.mp3'))
    return move_sound, capture_sound, check_sound, checkmate_sound, castle_sound

# Utility function to evaluate the board
def evaluate_board(board):
    eval = 0
    for piece_type in range(1, 7):
        eval += len(board.pieces(piece_type, chess.WHITE)) - len(board.pieces(piece_type, chess.BLACK))
    return eval

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if is_maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Get the best move for the current player
def get_best_move(board, depth):
    best_move = None
    best_value = float('-inf') if board.turn else float('inf')

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, float('-inf'), float('inf'), not board.turn)
        board.pop()

        if board.turn:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move

# Draw the board and pieces
def draw_board(screen, board, dragging_piece=None, dragging_pos=None):
    wood_colors = [pygame.Color(181, 136, 99), pygame.Color(240, 217, 181)]  # Wooden colors
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = wood_colors[(r+c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            piece = board.piece_at(chess.square(c, DIMENSION - 1 - r))
            if piece and (dragging_piece is None or chess.square(c, DIMENSION - 1 - r) != dragging_piece):
                piece_image = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
                screen.blit(IMAGES[piece_image], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
    if dragging_piece and dragging_pos:
        piece = board.piece_at(dragging_piece)
        piece_image = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
        screen.blit(IMAGES[piece_image], (dragging_pos[0] - SQ_SIZE // 2, dragging_pos[1] - SQ_SIZE // 2))

# Display check and checkmate messages
def display_message(screen, message):
    font = pygame.font.SysFont('Arial', 32, True, False)
    text = font.render(message, True, pygame.Color('Red'))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)

# Function to play the appropriate sound based on the move
def play_move_sound(move, board, move_sound, capture_sound, castle_sound):
    if board.is_capture(move):
        capture_sound.play()
    elif board.is_castling(move):
        castle_sound.play()
    else:
        move_sound.play()

# Main game loop with dragging logic
def play_game():
    board = chess.Board()
    load_images()
    move_sound, capture_sound, check_sound, checkmate_sound, castle_sound = load_sounds()
    running = True
    selected_square = None
    dragging_piece = None
    dragging_pos = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                square = chess.square(col, DIMENSION - 1 - row)

                if board.piece_at(square) and board.color_at(square) == board.turn:
                    dragging_piece = square
                    dragging_pos = location
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_piece is not None:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    square = chess.square(col, DIMENSION - 1 - row)

                    move = chess.Move(dragging_piece, square)
                    if move in board.legal_moves:
                        if board.piece_at(dragging_piece).piece_type == chess.PAWN and (square // 8 == 0 or square // 8 == 7):
                            move = chess.Move(dragging_piece, square, promotion=chess.QUEEN)
                        
                        play_move_sound(move, board, move_sound, capture_sound, castle_sound)
                        board.push(move)
                        
                        if board.is_check():
                            check_sound.play()
                            display_message(screen, "Check!")
                        
                        if board.is_checkmate():
                            checkmate_sound.play()
                            display_message(screen, "Checkmate!")
                            running = False
                        
                        if not board.is_game_over():
                            ai_move = get_best_move(board, 3)
                            if ai_move:
                                play_move_sound(ai_move, board, move_sound, capture_sound, castle_sound)
                                board.push(ai_move)
                                
                                if board.is_check():
                                    check_sound.play()
                                    display_message(screen, "Check!")
                                
                                if board.is_checkmate():
                                    checkmate_sound.play()
                                    display_message(screen, "Checkmate!")
                                    running = False
                    dragging_piece = None
                    dragging_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_piece is not None:
                    dragging_pos = pygame.mouse.get_pos()

        draw_board(screen, board, dragging_piece, dragging_pos)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    play_game()









