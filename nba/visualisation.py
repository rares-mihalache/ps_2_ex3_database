"""Plotting functions for the NBA insights notebook."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

# ---------------------------------------------------------------------
# Yvette: Finding 1 (home-court advantage) and Finding 2 (three-pointers)
# ---------------------------------------------------------------------

# Colour-blind-friendly colours (Okabe-Ito palette)
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREY = "#7F7F7F"


def plot_home_advantage_trend(df: pd.DataFrame) -> Figure:
    """Plot the home win rate and average attendance over time.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.home_win_by_season``.

    Returns
    -------
    Figure
        Two panels sharing the season axis: home win rate on top,
        average attendance (thousands) below.
    """
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(9, 6), sharex=True, height_ratios=[3, 2]
    )

    top.plot(df["season"], df["home_win_pct"], color=BLUE)
    top.axhline(50, color=GREY, linestyle="--", linewidth=1)
    top.text(1947, 51, "50% = no home advantage", color=GREY)
    top.set_ylim(40, 80)
    top.set_ylabel("Home teams' win rate (%)")
    top.set_title(
        "Crowds have tripled, yet home advantage has shrunk",
        loc="left",
        fontweight="bold",
    )

    bottom.plot(df["season"], df["avg_attendance"] / 1000, color=ORANGE)
    bottom.set_ylim(0, 20)
    bottom.set_ylabel("Average crowd\n(thousands)")
    bottom.set_xlabel("Season (start year)")
    bottom.annotate(
        "2020-21: most games\nplayed without fans",
        xy=(2020, 3),
        xytext=(1990, 3),
        arrowprops={"arrowstyle": "->", "color": GREY},
        color=GREY,
    )

    for ax in (top, bottom):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_home_win_by_setting(df: pd.DataFrame) -> Figure:
    """Plot the home win rate in each setting as horizontal bars.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.home_win_by_setting`` (already sorted).

    Returns
    -------
    Figure
        One bar per setting, with empty-arena games highlighted and a
        reference line at 50%.
    """
    df = df.iloc[::-1]  # largest bar at the top
    colours = [
        ORANGE if "empty" in setting else BLUE for setting in df["setting"]
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(df["setting"], df["home_win_pct"], color=colours)
    labels = [
        f"{pct:.1f}%  ({games:,} games)"
        for pct, games in zip(df["home_win_pct"], df["games"])
    ]
    ax.bar_label(bars, labels=labels, padding=4)
    ax.axvline(50, color=GREY, linestyle="--", linewidth=1)
    ax.set_xlim(0, 85)
    ax.set_xlabel(
        "Home teams' win rate (%)\n"
        "Regular season, preseason and playoffs: games since 2000-01"
    )
    ax.set_title(
        "Take the fans away and home advantage disappears",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_crowd_effects(df: pd.DataFrame) -> Figure:
    """Compare free throws with fans and in empty arenas (2020-21).

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.crowd_effects``.

    Returns
    -------
    Figure
        Left: the away team's free-throw percentage. Right: how many
        more free throws the home team got per game.
    """
    df = df.set_index("crowd").loc[["Fans", "Empty arena"]]
    colours = [BLUE, ORANGE]

    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 4))

    bars = left.bar(df.index, df["away_ft_pct"], color=colours)
    left.bar_label(bars, fmt="%.1f%%", padding=3)
    left.set_ylim(0, 100)
    left.set_title(
        "Away shooters don't miss more\nwith fans behind the basket",
        loc="left",
    )
    left.set_ylabel("Away team's free-throw %")

    bars = right.bar(df.index, df["extra_fta_home"], color=colours)
    right.bar_label(bars, fmt="%.2f", padding=3)
    right.set_ylim(0, 1.6)
    right.set_title(
        "but home teams get fewer extra\nfree throws without fans",
        loc="left",
    )
    right.set_ylabel("Extra free throws per game\n(home minus away)")

    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(
        "2020-21: how do crowds help the home team?",
        x=0.02,
        ha="left",
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def plot_three_point_trend(df: pd.DataFrame) -> Figure:
    """Plot the share of shots that are threes and three-point accuracy.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.threes_by_season``.

    Returns
    -------
    Figure
        Two panels sharing the season axis, each with one line for the
        regular season and one for the playoffs, labelled directly.
    """
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
    # label position: playoffs just above its line, regular season below
    styles = {
        "Regular Season": (BLUE, "top"),
        "Playoffs": (ORANGE, "bottom"),
    }

    for season_type, (colour, position) in styles.items():
        part = df[df["season_type"] == season_type]
        last = part.iloc[-1]
        top.plot(part["season"], part["three_share"], color=colour)
        top.text(
            last["season"] + 0.5,
            last["three_share"],
            season_type,
            color=colour,
            va=position,
        )
        bottom.plot(part["season"], part["three_pct"], color=colour)

    top.axvspan(1993.5, 1996.5, color=GREY, alpha=0.15)
    top.text(1993.7, 30, "Shorter\n3-point line\n1994-97", color=GREY)
    top.set_ylim(0, 45)
    top.set_ylabel("Threes as % of all shots")
    top.set_title(
        "Threes have gone from 4% to almost 40% of all shots,\n"
        "while accuracy has held at about 35% since the mid-1990s",
        loc="left",
        fontweight="bold",
    )

    bottom.set_ylim(0, 45)
    bottom.set_xlim(1984, 2030)  # room for the line labels
    bottom.set_ylabel("Three-point %")
    bottom.set_xlabel("Season (start year)")

    for ax in (top, bottom):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_three_point_win_rates(df: pd.DataFrame) -> Figure:
    """Plot how often the team with more threes wins, by season.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.threes_win_rates``.

    Returns
    -------
    Figure
        Two lines (made more threes, took more threes), labelled
        directly, with a reference line at 50%.
    """
    lines = {
        "more_threes_made_win_pct": ("Made more threes", BLUE),
        "more_threes_taken_win_pct": ("Took more threes", ORANGE),
    }

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for column, (label, colour) in lines.items():
        ax.plot(df["season"], df[column], color=colour)
        ax.text(
            df["season"].iloc[-1] + 0.5,
            df[column].iloc[-1],
            label,
            color=colour,
            va="center",
        )

    ax.axhline(50, color=GREY, linestyle="--", linewidth=1)
    ax.text(2010, 49.5, "50% = a coin flip", color=GREY, va="top")
    ax.set_ylim(20, 80)
    ax.set_xlim(1984, 2030)  # room for the line labels
    ax.set_ylabel("Win rate of that team (%)")
    ax.set_xlabel("Season (start year)")
    ax.set_title(
        "From desperation shot to winning weapon: making threes now "
        "wins,\ntaking more of them doesn't",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------
# Bryan: Finding 3 (how safe is a lead?) and Finding 4 (the global NBA)
# ---------------------------------------------------------------------


def plot_lead_safety(df: pd.DataFrame) -> Figure:
    """Plot how often the leader after three quarters wins, by lead size.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.lead_safety``.

    Returns
    -------
    Figure
        One bar per size of lead, with a reference line at 50%.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(df["lead_size"], df["leader_win_pct"], color=BLUE)
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.axhline(50, color=GREY, linestyle="--", linewidth=1)
    ax.text(4.55, 51, "50% =\na coin flip", color=GREY)
    ax.set_xlim(-0.6, 5.3)  # room for the reference line label
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 101, 20))
    ax.set_xlabel("Lead after three quarters (points)")
    ax.set_ylabel("Leading team's win rate (%)")
    ax.set_title(
        "A small lead is far from safe,\n"
        "but from 11 points up the leader wins over 90% of the time",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_blown_leads_by_decade(df: pd.DataFrame) -> Figure:
    """Plot how often a lead of 10 or more is lost, by decade.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.blown_leads_by_decade``.

    Returns
    -------
    Figure
        One bar per decade, labelled with the rate and the games behind it.
    """
    fig, ax = plt.subplots(figsize=(10.5, 4.5))
    bars = ax.bar(df["decade"], df["blown_pct"], color=BLUE)
    labels = [
        f"{pct:.1f}%\n({blown} of {games:,})"
        for pct, blown, games in zip(df["blown_pct"], df["blown"], df["games"])
    ]
    ax.bar_label(bars, labels=labels, padding=3, fontsize=9)
    ax.set_ylim(0, 7)
    ax.set_xlabel("Decade (the 2020s end in June 2023)")
    ax.set_ylabel("Leads of 10+ lost (%)")
    ax.set_title(
        "Big leads are getting less safe: since the 1980s, the share "
        "of\n10+ point leads lost after three quarters has kept rising",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_international_share(df: pd.DataFrame) -> Figure:
    """Plot the share of new players from outside the USA, by decade.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.international_share``.

    Returns
    -------
    Figure
        One bar per decade, labelled with the share and the number of
        countries players came from, including the USA.
    """
    fig, ax = plt.subplots(figsize=(9, 4.5))
    decades = [f"{decade}s" for decade in df["decade"]]
    bars = ax.bar(decades, df["international_pct"], color=BLUE)
    labels = [
        f"{pct:.1f}%\n{n} {'country' if n == 1 else 'countries'}"
        for pct, n in zip(df["international_pct"], df["countries"])
    ]
    ax.bar_label(bars, labels=labels, padding=3, fontsize=9)
    ax.set_ylim(0, 30)
    ax.set_xlabel(
        "Decade the player joined (the 2020s end in 2022). "
        "Country counts include the USA."
    )
    ax.set_ylabel("Players from outside the USA (%)")
    ax.set_title(
        "The NBA went global: almost no international players before "
        "the 1980s,\nabout one new player in four by the 2010s",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_top_countries(df: pd.DataFrame) -> Figure:
    """Plot the countries outside the USA with the most NBA players.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``wrangling.top_countries`` (already sorted).

    Returns
    -------
    Figure
        One horizontal bar per country, labelled with the number of
        players and the year the first of them joined.
    """
    df = df.iloc[::-1]  # largest bar at the top
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(df["country"], df["players"], color=BLUE)
    labels = [
        f"{players}  (first in {year})"
        for players, year in zip(df["players"], df["first_year"])
    ]
    ax.bar_label(bars, labels=labels, padding=4)
    ax.set_xlim(0, 48)
    ax.set_xlabel("NBA players in the data")
    ax.set_title(
        "Canada has the most NBA players outside the USA,\n"
        "but France nearly matches it after arriving only in 2000",
        loc="left",
        fontweight="bold",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig
