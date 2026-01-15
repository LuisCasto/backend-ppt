import random

class GameLogic:
    """Lógica del juego Piedra, Papel o Tijera"""
    
    @staticmethod
    def evaluate_round(player_move: int, cpu_move: int) -> str:
        """
        Evalúa quién gana la ronda
        Returns: 'player', 'cpu', o 'tie'
        """
        # Empate
        if player_move == cpu_move:
            return "tie"
        
        # Victorias del jugador
        winning_moves = {
            (1, 3),  # Piedra vs Tijera
            (2, 1),  # Papel vs Piedra
            (3, 2),  # Tijera vs Papel
        }
        
        if (player_move, cpu_move) in winning_moves:
            return "player"
        else:
            return "cpu"
    
    @staticmethod
    def get_cpu_move_normal() -> int:
        """Modo Normal: jugada aleatoria"""
        return random.randint(1, 3)
    
    @staticmethod
    def get_cpu_move_imposible(player_move: int) -> int:
        """
        Modo Imposible: 80% de probabilidad de ganar
        20% de probabilidad de jugar random
        """
        chance = random.randint(0, 100)
        
        if chance < 20:
            # 20% random
            return random.randint(1, 3)
        else:
            # 80% gana la CPU
            winning_counter = {
                1: 2,  # Si jugador usa Piedra, CPU usa Papel
                2: 3,  # Si jugador usa Papel, CPU usa Tijera
                3: 1   # Si jugador usa Tijera, CPU usa Piedra
            }
            return winning_counter[player_move]
    
    @staticmethod
    def calculate_score(player_wins: int, cpu_wins: int, ties: int) -> int:
        """Calcula el puntaje final"""
        return (player_wins * 100) - (cpu_wins * 100) + (ties * 25)