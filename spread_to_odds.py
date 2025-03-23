#!/usr/bin/env python3
import argparse
import math

def translate_spread_to_probability(spread, total=None, sigma=10):
    """
    Translates a betting spread (and optionally a total points line) into win probability.

    Parameters:
        spread (float): The betting spread for the favorite (e.g., -8.5).
        total (float, optional): The total points line for the game.
        sigma (float): The standard deviation for the point differential (default is 10).

    Returns:
        float: Win probability (0 to 1) if total is None.
        tuple: (win probability, (favorite score, underdog score)) if total is provided.
    """
    # Use the absolute value of the spread for calculation.
    margin = abs(spread)
    # Calculate the z-score assuming the point differential is normally distributed.
    z = margin / sigma
    # Compute win probability using the normal cumulative distribution function.
    probability = 0.5 + 0.5 * math.erf(z / math.sqrt(2))
    
    if total is not None:
        # Calculate expected scores if total is provided.
        favorite_score = (total + margin) / 2
        underdog_score = (total - margin) / 2
        return probability, (favorite_score, underdog_score)
    else:
        return probability

def main():
    parser = argparse.ArgumentParser(
        description="Translate a betting spread and optionally a total into win probability."
    )
    parser.add_argument("spread", type=float, help="Betting spread (e.g., -8.5 for a favorite).")
    parser.add_argument("--total", type=float, default=None,
                        help="Optional total points for the game (e.g., 150.5).")

    args = parser.parse_args()

    result = translate_spread_to_probability(args.spread, args.total)
    if args.total is not None:
        probability, (fav_score, underdog_score) = result
        print(f"Win Probability: {probability:.2%}")
        print(f"Expected Favorite Score: {fav_score:.2f}")
        print(f"Expected Underdog Score: {underdog_score:.2f}")
    else:
        probability = result
        print(f"Win Probability: {probability:.2%}")

if __name__ == "__main__":
    main()
