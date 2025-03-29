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

def calculate_odds(team1_net_rating, team2_net_rating, location="neutral", home_court_advantage=3):
    """
    Calculates the point spread and implied win probabilities based on Net Ratings.

    Args:
        team1_net_rating (float): Net Rating of team 1.
        team2_net_rating (float): Net Rating of team 2.
        location (str): The location of the game. Options are "home", "away", or "neutral".
        home_court_advantage (float): Value of home court advantage in points.

    Returns:
        tuple: (point_spread, team1_win_probability, team2_win_probability)
               Point spread is from the perspective of team 1.
               Win probabilities are percentages.
    """
    net_rating_diff = team1_net_rating - team2_net_rating
    point_spread = net_rating_diff  # Default to neutral court

    # Adjust for home court advantage
    if location == "home":
        point_spread += home_court_advantage
    elif location == "away":
        point_spread -= home_court_advantage

    # Convert point spread to win probability using a logistic function approximation
    probability_team1_wins = 1 / (1 + math.exp(-0.4 * point_spread))
    probability_team2_wins = 1 - probability_team1_wins

    return point_spread, probability_team1_wins * 100, probability_team2_wins * 100

def convert_probability_to_american_odds(probability):
    """Converts a win probability (0 to 1) to American odds."""
    if probability == 0:
        return float('inf')
    if probability == 1:
        return float('-inf')

    if probability >= 0.5:
        return round(-100 * probability / (1 - probability))
    else:
        return round(100 * (1 - probability) / probability)

if __name__ == "__main__":
    team1_name = input("Enter the name of Team 1: ")
    team2_name = input("Enter the name of Team 2: ")

    while True:
        try:
            team1_net_rating = float(input(f"Enter the NetRtg for {team1_name}: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for NetRtg.")

    while True:
        try:
            team2_net_rating = float(input(f"Enter the NetRtg for {team2_name}: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for NetRtg.")

    while True:
        location_input = input(f"Enter the game location (home, away, or neutral for {team1_name}): ").lower()
        if location_input in ["home", "away", "neutral"]:
            location = location_input
            break
        else:
            print("Invalid input. Please enter 'home', 'away', or 'neutral'.")

    point_spread, team1_win_prob, team2_win_prob = calculate_odds(
        team1_net_rating, team2_net_rating, location=location
    )

    # Calculate implied probability from the spread
    implied_probability_team1_from_spread = translate_spread_to_probability(point_spread)

    team1_odds_american = convert_probability_to_american_odds(team1_win_prob / 100)
    team2_odds_american = convert_probability_to_american_odds(team2_win_prob / 100)

    print(f"\nMatchup: {team1_name} vs {team2_name}")
    print(f"Game Location for {team1_name}: {location.capitalize()}")
    print(f"Point Spread ({team1_name} as favorite): {point_spread:.2f}")
    print(f"{team1_name} Win Probability (based on NetRtg): {team1_win_prob:.2f}%")
    print(f"{team2_name} Win Probability (based on NetRtg): {team2_win_prob:.2f}%")
    print(f"{team1_name} Implied Win Probability (from spread): {implied_probability_team1_from_spread:.4f}")
    print(f"{team1_name} American Odds: {team1_odds_american}")
    print(f"{team2_name} American Odds: {team2_odds_american}")