"""Plotting functions for the NBA insights notebook."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

# ---------------------------------------------------------------------
# Bryan: Finding 3 (how safe is a lead?) and Finding 4 (the global NBA)
# ---------------------------------------------------------------------

# Same colour-blind-friendly colours as Findings 1 and 2 (Okabe-Ito)
BLUE = "#0072B2"
GREY = "#7F7F7F"


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
