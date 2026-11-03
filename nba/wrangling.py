"""Functions that query the NBA database and tidy the results."""

import sqlite3

import pandas as pd

# ---------------------------------------------------------------------
# Yvette: Finding 1 (home-court advantage) and Finding 2 (three-pointers)
# ---------------------------------------------------------------------

# Attendance is only recorded for most games from the 1962-63 season on.
FIRST_ATTENDANCE_SEASON = 1962

HOME_WIN_BY_SEASON_QUERY = """
SELECT CAST(SUBSTR(g.season_id, 2) AS INTEGER) AS season,
       COUNT(*) AS games,
       100.0 * AVG(g.wl_home = 'W') AS home_win_pct,
       AVG(i.attendance) AS avg_attendance
FROM game AS g
LEFT JOIN (
    -- one row per game: a few games are stored twice in game_info
    SELECT game_id, MAX(CAST(attendance AS INTEGER)) AS attendance
    FROM game_info
    GROUP BY game_id
) AS i
    ON g.game_id = i.game_id
WHERE g.season_type = 'Regular Season'
GROUP BY season
ORDER BY season
"""

HOME_WIN_BY_SETTING_QUERY = """
SELECT 'Regular season' AS setting,
       COUNT(*) AS games,
       100.0 * AVG(wl_home = 'W') AS home_win_pct
FROM game
WHERE season_type = 'Regular Season'
  AND game_date >= '2000-07-01'

UNION ALL

SELECT 'Preseason', COUNT(*), 100.0 * AVG(wl_home = 'W')
FROM game
WHERE season_type = 'Pre Season'
  AND game_date >= '2000-07-01'

UNION ALL

SELECT 'Playoffs', COUNT(*), 100.0 * AVG(wl_home = 'W')
FROM game
WHERE season_type = 'Playoffs'
  AND game_date >= '2000-07-01'

UNION ALL

-- All-Star games are stored under two spellings and often twice,
-- so keep one row per game before counting
SELECT 'All-Star', COUNT(*), 100.0 * AVG(wl_home = 'W')
FROM (
    SELECT DISTINCT game_date, team_name_home, team_name_away, wl_home
    FROM game
    WHERE season_type IN ('All Star', 'All-Star')
)

UNION ALL

-- 2020-21: no attendance record (or 0) means an empty arena
SELECT CASE
           WHEN i.attendance IS NULL OR i.attendance = 0
               THEN '2020-21, empty arena'
           ELSE '2020-21, fans'
       END AS setting,
       COUNT(*),
       100.0 * AVG(g.wl_home = 'W')
FROM game AS g
LEFT JOIN (
    SELECT game_id, MAX(CAST(attendance AS INTEGER)) AS attendance
    FROM game_info
    GROUP BY game_id
) AS i
    ON g.game_id = i.game_id
WHERE g.season_type = 'Regular Season'
  AND g.season_id = '22020'
GROUP BY setting
"""

CROWD_EFFECTS_QUERY = """
SELECT CASE
           WHEN i.attendance IS NULL OR i.attendance = 0
               THEN 'Empty arena'
           ELSE 'Fans'
       END AS crowd,
       COUNT(*) AS games,
       100.0 * AVG(g.wl_home = 'W') AS home_win_pct,
       AVG(g.fta_home - g.fta_away) AS extra_fta_home,
       AVG(g.pf_away - g.pf_home) AS extra_fouls_away,
       100.0 * SUM(g.ftm_home) / SUM(g.fta_home) AS home_ft_pct,
       100.0 * SUM(g.ftm_away) / SUM(g.fta_away) AS away_ft_pct
FROM game AS g
LEFT JOIN (
    SELECT game_id, MAX(CAST(attendance AS INTEGER)) AS attendance
    FROM game_info
    GROUP BY game_id
) AS i
    ON g.game_id = i.game_id
WHERE g.season_type = 'Regular Season'
  AND g.season_id = '22020'
GROUP BY crowd
"""

SAME_TEAM_CROWD_GAP_QUERY = """
WITH by_team AS (
    SELECT g.team_id_home AS team_id,
           CASE
               WHEN i.attendance IS NULL OR i.attendance = 0
                   THEN 'empty'
               ELSE 'fans'
           END AS crowd,
           AVG(g.wl_home = 'W') AS win_rate
    FROM game AS g
    LEFT JOIN (
        SELECT game_id, MAX(CAST(attendance AS INTEGER)) AS attendance
        FROM game_info
        GROUP BY game_id
    ) AS i
        ON g.game_id = i.game_id
    WHERE g.season_type = 'Regular Season'
      AND g.season_id = '22020'
    GROUP BY team_id, crowd
)
SELECT COUNT(*) AS teams_with_both,
       100.0 * AVG(f.win_rate - e.win_rate) AS avg_gap_pct_points
FROM by_team AS f
JOIN by_team AS e
    ON f.team_id = e.team_id
WHERE f.crowd = 'fans'
  AND e.crowd = 'empty'
"""

THREES_BY_SEASON_QUERY = """
SELECT CAST(SUBSTR(season_id, 2) AS INTEGER) AS season,
       season_type,
       COUNT(*) AS games,
       100.0 * SUM(fg3a_home + fg3a_away)
             / SUM(fga_home + fga_away) AS three_share,
       100.0 * SUM(fg3m_home + fg3m_away)
             / SUM(fg3a_home + fg3a_away) AS three_pct
FROM game
WHERE season_type IN ('Regular Season', 'Playoffs')
  AND game_date >= '1985-07-01'
GROUP BY season, season_type
ORDER BY season, season_type
"""

THREES_WIN_RATES_QUERY = """
SELECT CAST(SUBSTR(season_id, 2) AS INTEGER) AS season,
       COUNT(*) AS games,
       -- 1 if the team that made more threes won, 0 if it lost;
       -- no ELSE, so games with equal threes are NULL and AVG skips them
       100.0 * AVG(CASE
           WHEN fg3m_home > fg3m_away THEN wl_home = 'W'
           WHEN fg3m_home < fg3m_away THEN wl_home = 'L'
       END) AS more_threes_made_win_pct,
       100.0 * AVG(CASE
           WHEN fg3a_home > fg3a_away THEN wl_home = 'W'
           WHEN fg3a_home < fg3a_away THEN wl_home = 'L'
       END) AS more_threes_taken_win_pct
FROM game
WHERE season_type = 'Regular Season'
  AND game_date >= '1985-07-01'
GROUP BY season
ORDER BY season
"""


def home_win_by_season(con: sqlite3.Connection) -> pd.DataFrame:
    """Home win rate and average attendance for each regular season.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row per season with columns season, games, home_win_pct and
        avg_attendance. Attendance is set to missing before 1962, when
        only a handful of games have it recorded.
    """
    df = pd.read_sql(HOME_WIN_BY_SEASON_QUERY, con)
    early = df["season"] < FIRST_ATTENDANCE_SEASON
    df.loc[early, "avg_attendance"] = float("nan")
    return df


def home_win_by_setting(con: sqlite3.Connection) -> pd.DataFrame:
    """Home win rate in different settings, from most to least.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row per setting (regular season, preseason and playoffs
        since 2000-01, All-Star games, and 2020-21 games with and
        without fans) with columns setting, games and home_win_pct.
    """
    df = pd.read_sql(HOME_WIN_BY_SETTING_QUERY, con)
    df = df.sort_values("home_win_pct", ascending=False)
    return df.reset_index(drop=True)


def crowd_effects(con: sqlite3.Connection) -> pd.DataFrame:
    """Compare 2020-21 games with fans and in empty arenas.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row per crowd type ("Fans", "Empty arena") with the home
        win rate, the home team's extra free-throw attempts, the away
        team's extra fouls, and both teams' free-throw percentages.
    """
    return pd.read_sql(CROWD_EFFECTS_QUERY, con)


def same_team_crowd_gap(con: sqlite3.Connection) -> pd.DataFrame:
    """Average gap in home win rate with fans vs empty arenas, by team.

    Each team is compared with itself in 2020-21, so differences in team
    strength cancel out.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row with the number of teams that played home games both
        with and without fans, and the average gap in percentage points.
    """
    return pd.read_sql(SAME_TEAM_CROWD_GAP_QUERY, con)


def threes_by_season(con: sqlite3.Connection) -> pd.DataFrame:
    """Share of shots that are threes, and three-point accuracy.

    Starts in 1985-86, the first season with complete three-point data.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row per season and season type (regular season, playoffs)
        with columns season, season_type, games, three_share (percent
        of all shots) and three_pct (percent of threes made).
    """
    return pd.read_sql(THREES_BY_SEASON_QUERY, con)


def threes_win_rates(con: sqlite3.Connection) -> pd.DataFrame:
    """How often the team with more threes wins, by season.

    Parameters
    ----------
    con : sqlite3.Connection
        Open connection to the NBA database.

    Returns
    -------
    pd.DataFrame
        One row per regular season since 1985-86 with the win rate of
        the team that made more threes and of the team that took more
        threes. Games where both teams had the same number are left out.
    """
    return pd.read_sql(THREES_WIN_RATES_QUERY, con)
