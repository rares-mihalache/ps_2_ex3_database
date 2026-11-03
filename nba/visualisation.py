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
