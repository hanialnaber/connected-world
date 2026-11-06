"""World Football Elo ratings, rebuilt from every international result since 1872.

Method (eloratings.net): R_new = R_old + K * G * (W - W_e), where W_e = 1 / (10^(-dr/400) + 1),
dr includes +100 for the home side unless the venue is neutral, K depends on the match's stakes
and G grows with the goal margin. Only teams recognised by FIFA (they have played World Cup
qualifying since 2010) and their matches against each other are rated, so regional and
diaspora sides never enter the ratings.
"""
import pandas as pd

CONTINENTAL_FINALS = {
    "UEFA Euro", "Copa América", "African Cup of Nations", "AFC Asian Cup", "Gold Cup",
    "CONCACAF Championship", "OFC Nations Cup", "Confederations Cup",
}


def k_factor(tournament: str) -> int:
    if tournament == "FIFA World Cup":
        return 60
    if tournament in CONTINENTAL_FINALS:
        return 50
    if "qualification" in tournament or "Nations League" in tournament:
        return 40
    if tournament == "Friendly":
        return 20
    return 30


def margin_factor(goal_diff: int) -> float:
    n = abs(goal_diff)
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    return (11 + n) / 8


def model(dbt, session):
    dbt.config(materialized="table")
    m = dbt.ref("stg_football__results").df()
    wc = m[m.tournament.isin(["FIFA World Cup", "FIFA World Cup qualification"]) & (pd.to_datetime(m.match_date) >= pd.Timestamp("2010-01-01"))]
    recognised = (set(wc.home_team) | set(wc.away_team))
    codes = dict(zip(m.home_team, m.home_code)) | dict(zip(m.away_team, m.away_code))
    recognised = {t for t in recognised if isinstance(codes.get(t), str)}

    m = m[m.home_team.isin(recognised) & m.away_team.isin(recognised)].sort_values(["match_date", "match_id"])
    rating: dict[str, float] = {}
    rows = []
    for r in m.itertuples(index=False):
        rh, ra = rating.get(r.home_team, 1500.0), rating.get(r.away_team, 1500.0)
        dr = rh - ra + (0 if r.is_neutral else 100)
        expected_home = 1 / (10 ** (-dr / 400) + 1)
        result_home = 1.0 if r.home_score > r.away_score else (0.5 if r.home_score == r.away_score else 0.0)
        change = k_factor(r.tournament) * margin_factor(r.home_score - r.away_score) * (result_home - expected_home)
        rating[r.home_team], rating[r.away_team] = rh + change, ra - change
        rows.append((r.match_id, r.match_date, r.home_team, codes[r.home_team], rh, rh + change, change))
        rows.append((r.match_id, r.match_date, r.away_team, codes[r.away_team], ra, ra - change, -change))
    out = pd.DataFrame(rows, columns=["match_id", "match_date", "team", "team_code", "rating_before", "rating_after", "rating_change"])
    # DuckDB reads pandas' new "str" dtype only as plain objects
    return out.astype({"team": object, "team_code": object})
