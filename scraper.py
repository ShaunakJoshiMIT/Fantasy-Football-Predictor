import requests
from bs4 import BeautifulSoup
from typing import List
import time
import csv

def scrape_data(csv_name, stat_categories: List[str]):
    """
    Scrapes player data and writes to csv: csv_name
    """

    url = "https://www.pro-football-reference.com/years/2023/scrimmage.htm"
    page = requests.get(url)
    if not page.ok:
        print(str(page))
        return
    with open(csv_name, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "fantasy_ppr"] + stat_categories)

    soup = BeautifulSoup(page.text, features="html.parser")
    table = soup.find("table", class_="per_match_toggle")
    tbody = table.find('tbody')
    players = tbody.find_all("tr")

    for player in players:
        data = player.find("td")

        try:
            link = data.find("a")
            pos = player.find("td", attrs = {"data-stat": "pos"}).text
            if pos == "QB":
                continue
        except AttributeError:
            continue

        name, href = link.text, "https://www.pro-football-reference.com" + link["href"]
        try:
            player_training_data = recursive_averages(get_player_data(href))
        except:
            continue

        if not player_training_data:
            continue

        for i, data in enumerate(player_training_data):
            print(name)
            with open(csv_name, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, data["fantasy_ppr"]] + [data[cat] for cat in stat_categories if cat != "fantasy_ppr"])

def get_player_data(url):
    """
    Fetches player data from url, returns list of dictionaries

    Excludes unecessary datapoints and makes sure the data can be worked with.
    """
    time.sleep(2.5)
    page = requests.get(url)
    if not page.ok:
        print(page)
        return []

    soup = BeautifulSoup(page.text, features="html.parser")
    tbody = soup.find("tbody")
    seasons = tbody.find_all("tr", class_ = "full_table")
    out = []
    for season in seasons:
        stats = season.find_all("td")[4:33] #skips unneccessary categories
        stats_dict = {}
        for stat in stats:
            if "per_g" in stat["data-stat"]:
                continue
            val = stat.text.strip("%") if stat.text.strip("%") else 0
            stats_dict[stat["data-stat"]] = float(val)

        stats_dict["fantasy_ppr"] = calculate_ppr(stats_dict)
        out.append(stats_dict)
    out.reverse() # Orders in descending order. e.g. [2020, 2019, 2018]

    return out

def recursive_averages(stats_ppr: List[dict]):
    """
    Recursively finds a given players career averages at each point in their career.
    Will present the players fantasy points for that year and that players career averages
    going into that season.
    """

    if not stats_ppr:
        return []
    elif len(stats_ppr) <= 1:
        return []

    first = stats_ppr[0]
    stat_categories = first.keys()
    prev_average_stats = {}
    prev_game_sum = sum(stat["g"] for stat in stats_ppr[1:])

    for cat in stat_categories:
        if cat in {"g", "gs", "fantasy_ppr"}:
            continue
        if "per" in cat:
            prev_average_stats[cat] = sum(stat[cat] for stat in stats_ppr[1:]) / len(stats_ppr[1:])
        else:
            prev_average_stats[cat] = sum(stat[cat] for stat in stats_ppr[1:])/prev_game_sum
    prev_average_stats["fantasy_ppr"] = first["fantasy_ppr"]

    return [prev_average_stats] + recursive_averages(stats_ppr[1:])

def calculate_ppr(stats: dict):
    """
    Calculates given players fantasy ppr points
    """
    points = (stats["rush_yds"] * 0.1) + (stats["rush_td"] * 6) + (stats["rec_yds"] * 0.1) + (stats["rec_td"] * 6) + (stats["rec"]) - (stats["fumbles"] * 2)
    return round(points,1)

def get_career_averages(csv_name, stat_categories, seen = set()):
    """
    Calculates career average stats for each player, writing to a csv.

    can skip players in seen
    """
    url = "https://www.pro-football-reference.com/years/2023/scrimmage.htm"
    page = requests.get(url)
    if not page.ok:
        print(str(page))
        return
    soup = BeautifulSoup(page.text, features="html.parser")
    table = soup.find("table", class_="per_match_toggle")
    tbody = table.find('tbody')
    players = tbody.find_all("tr")

    # with open(csv_name, "w", newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["name"] + stat_categories)

    for player in players:

        data = player.find("td")

        try:
            link = data.find("a")
            pos = player.find("td", attrs = {"data-stat": "pos"}).text
            if pos == "QB":
                continue
        except AttributeError:
            continue

        name, href = link.text, "https://www.pro-football-reference.com" + link["href"]
        print(name)
        if name in seen:
            continue
        try:
            data = get_player_data(href)
        except:
            continue
        averages = career_average(data)
        with open(csv_name, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name] + [averages[cat] for cat in stat_categories if cat != "fantasy_ppr"])
        # """
        #     writer.writerow([name, data["fantasy_ppr"]] + [data[cat] for cat in stat_categories if cat != "fantasy_ppr"])

        # """

def career_average(data):
    """
    Calculates career average given the data
    """
    first = data[0]
    categories = first.keys()
    average_stats = {}
    game_sum = sum(stat["g"] for stat in data)
    for cat in categories:
        if cat in {"g", "gs", "fantasy_ppr"}:
            continue
        if "per" in cat:
            average_stats[cat] = sum(stat[cat] for stat in data) / len(data)
        else:
            average_stats[cat] = sum(stat[cat]for stat in data) / game_sum
    # average_stats["fantasy_ppr"]
    return average_stats


if __name__ == "__main__":
    keys = ['rush_att', 'rush_yds', 'rush_td', 'rush_first_down', 'rush_success', 'rush_long', 'rush_yds_per_att', 'targets', 'rec', 'rec_yds', 'rec_yds_per_rec', 'rec_td', 'rec_first_down', 'rec_success', 'rec_long', 'catch_pct', 'rec_yds_per_tgt', 'touches', 'yds_per_touch', 'yds_from_scrimmage', 'rush_receive_td', 'fumbles', 'av', 'fantasy_ppr']
    csv_name = "train3.csv"
    seen = set()
    get_career_averages("averages.csv", keys, seen)
