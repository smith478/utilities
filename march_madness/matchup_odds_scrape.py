import requests
from bs4 import BeautifulSoup
import pandas as pd
import math

def scrape_kenpom_data():
    """Scrapes the KenPom ratings table from the website."""
    url = "https://kenpom.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main ratings table. This might require inspection of the KenPom website's HTML.
        # Based on typical KenPom structure, the table might have an ID like "ratings-table" or a class.
        # You'll need to adjust the selector based on the actual HTML.
        table = soup.find('table', {'id': 'ratings-table'}) # Example selector, adjust as needed

        if table:
            df = pd.read_html(str(table))[0]
            # Clean up the dataframe (e.g., rename columns, drop unnecessary rows)
            # This will depend on the exact structure of the scraped table.
            df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
            df = df.drop(index=0) # Drop header row if necessary
            return df
        else:
            print("Could not find the ratings table on KenPom.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during request to KenPom: {e}")
        return None
    except ValueError:
        print("No tables found in the HTML content.")
        return None

def calculate_odds(team1_net_rating, team2_net_rating, is_team1_home=False, home_court_advantage=3):
    """
    Calculates the point spread and implied win probabilities based on Net Ratings.

    Args:
        team1_net_rating (float): Net Rating of team 1.
        team2_net_rating (float): Net Rating of team 2.
        is_team1_home (bool): True if team 1 is playing at home, False otherwise.
        home_court_advantage (float): Value of home court advantage in points.

    Returns:
        tuple: (point_spread, team1_win_probability, team2_win_probability)
               Point spread is from the perspective of team 1.
               Win probabilities are percentages.
    """
    net_rating_diff = team1_net_rating - team2_net_rating

    # Adjust for home court advantage
    if is_team1_home:
        point_spread = net_rating_diff + home_court_advantage
    else:
        point_spread = net_rating_diff - home_court_advantage

    # Convert point spread to win probability using a logistic function approximation
    # This is a common approximation, but more sophisticated models exist.
    # The constants (4.5 and 0.4) are rough estimates based on historical data.
    # You might need to calibrate these based on your own analysis.
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
    kenpom_data = scrape_kenpom_data()

    if kenpom_data is not None:
        print("Successfully scraped KenPom data:")
        print(kenpom_data[['Team', 'NetRtg']].head())  # Display first few rows with relevant info

        # Example usage: Calculate odds for a hypothetical matchup
        team1_name = "Duke"
        team2_name = "Florida"

        team1_data = kenpom_data[kenpom_data['Team'].str.contains(team1_name, case=False, na=False)].iloc[0]
        team2_data = kenpom_data[kenpom_data['Team'].str.contains(team2_name, case=False, na=False)].iloc[0]

        team1_net_rating = float(team1_data['NetRtg'])
        team2_net_rating = float(team2_data['NetRtg'])

        # Assuming Duke is playing at home
        point_spread, team1_win_prob, team2_win_prob = calculate_odds(
            team1_net_rating, team2_net_rating, is_team1_home=True
        )

        team1_odds_american = convert_probability_to_american_odds(team1_win_prob / 100)
        team2_odds_american = convert_probability_to_american_odds(team2_win_prob / 100)

        print(f"\nMatchup: {team1_name} vs {team2_name}")
        print(f"Point Spread ({team1_name} as favorite): {point_spread:.2f}")
        print(f"{team1_name} Win Probability: {team1_win_prob:.2f}%")
        print(f"{team2_name} Win Probability: {team2_win_prob:.2f}%")
        print(f"{team1_name} American Odds: {team1_odds_american}")
        print(f"{team2_name} American Odds: {team2_odds_american}")
    else:
        print("Failed to retrieve KenPom data. Please check for errors.")