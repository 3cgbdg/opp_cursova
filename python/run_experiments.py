import time
import statistics
from services.core import ReversiCore

def run_experiment(num_games: int, difficulty_b: int, difficulty_w: int):
    """
    Runs num_games between two AIs (or Random if difficulty=0).
    difficulty_b: Black player depth (0 = random/first available - weak)
    difficulty_w: White player depth (0 = random/weak)
    """
    
    # Note: Our simple AI implementation doesn't have explicit "Random" mode exposed via API directly
    # except that depth 1 is very fast. For true random we might need to add it, but for now
    # let's assume Depth 1 is "Easy/Random-ish" and Depth 3+ is "AI".
    # Or we can just just Depth 1 vs Depth 3.
    
    results = {"Black": 0, "White": 0, "Draw": 0}
    times = []
    
    print(f"Running {num_games} games: Black(Depth {difficulty_b}) vs White(Depth {difficulty_w})...")
    
    for i in range(num_games):
        core = ReversiCore()
        # core.reset() is called in constructor typically or just new instance
        
        start_time = time.time()
        while core.result() == 0:
            current_player = core.current_player() # 1 or -1
            depth = difficulty_b if current_player == 1 else difficulty_w
            
            # If depth 0, we could pick random move, but let's just use depth 1 as 'weak'
            # or actually use get_valid_moves and pick random if we want rigorous exp.
            # For simplicity, we use API get_best_move with depth.
            
            r, c = core.get_best_move(max(1, depth))
            if r != -1:
                core.make_move(r, c)
            else:
                core.pass_turn()
        
        duration = time.time() - start_time
        times.append(duration)
        
        res = core.result()
        if res == 1: results["Black"] += 1
        elif res == -1: results["White"] += 1
        else: results["Draw"] += 1
        
        if (i + 1) % 5 == 0:
            print(f"Completed {i + 1}/{num_games} games...")
            
    print("\nResults:")
    print(f"Black Wins: {results['Black']} ({results['Black']/num_games*100:.1f}%)")
    print(f"White Wins: {results['White']} ({results['White']/num_games*100:.1f}%)")
    print(f"Draws: {results['Draw']}")
    print(f"Avg Game Time: {statistics.mean(times):.4f}s")
    print("-" * 40)

def main():
    # Experiment 1: Weak vs Weak (Depth 1 vs Depth 1)
    run_experiment(20, 1, 1)

    # Experiment 2: Weak vs Strong (Depth 1 vs Depth 4)
    run_experiment(20, 1, 4)

    # Experiment 3: Strong vs Weak (Depth 4 vs Depth 1)
    run_experiment(20, 4, 1)

if __name__ == "__main__":
    main()
