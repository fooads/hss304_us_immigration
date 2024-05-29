import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches



edge_color = "#30011E"
background_color = "#fafafa"

sns.set_style({
    "font.family": "serif",
    "figure.facecolor": background_color,
    "axes.facecolor": background_color,
})


def translate_geometries(df, x, y, scale, rotate):
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)
    return df


def adjust_maps(df):
    df_main_land = df[~df.STATEFP.isin(["02", "15"])]
    df_alaska = df[df.STATEFP == "02"]
    df_hawaii = df[df.STATEFP == "15"]

    df_alaska = translate_geometries(df_alaska, 1300000, -4900000, 0.5, 32)
    df_hawaii = translate_geometries(df_hawaii, 5400000, -1500000, 1, 24)

    return pd.concat([df_main_land, df_alaska, df_hawaii])


states = gpd.read_file("./data/")
states = states[~states.STATEFP.isin(["72", "69", "60", "66", "78"])]
states = states.to_crs("ESRI:102003")
states = adjust_maps(states)


states.loc[:, "color"] = "#880808"
states = states.sort_values(by='GEOID')


# Change file
# lpr = pd.read_csv("./statescsv.csv")
lpr = pd.read_csv("./passport.csv")

merged = pd.merge(states, lpr, on='STUSPS')


def create_color(df, column):
    colors = []
    for index, row in df.iterrows():

        value = row[column]

        if value > 0:
            colors.append(mcolors.to_hex((1 - abs(value) / 100, 1, 1 - abs(value) / 100)))
        else:
            colors.append(mcolors.to_hex((1, 1 - abs(value) / 100, 1 - abs(value) / 100)))

    return colors



for i in range(2014, 2023):
    year = str(i)
    merged.loc[:, "color"] = create_color(merged, year)

    ax = merged.plot(edgecolor=edge_color + "55", color=merged.color, figsize=(20, 20))
    merged.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)

    plt.axis("off")

    plt.annotate(
        text="U.S. Passport recipients change",
        xy=(0.5, 1.1), xycoords="axes fraction", fontsize=16, ha="center"
    )

    plt.annotate(
        text=f"{year}",
        xy=(0.5, 1.03), xycoords="axes fraction", fontsize=32, ha="center",
        fontweight="bold"
    )

    plt.annotate(
        "Change of U.S. citizenship\nrecipients relative to previous year.",
        xy=(0.5, -0.08), xycoords="axes fraction", ha="center", va="top", fontsize=18, linespacing=1.8
    )

    plt.annotate(
        "Source: https://www.dhs.gov/ohss/topics/immigration/yearbook/2022",
        xy=(0.5, -0.22), xycoords="axes fraction", fontsize=16, ha="center",
        fontweight="bold"
    )

    positive_patch = mpatches.Patch(color=(0.2, 0.8, 0.2), label='Positive Change')
    negative_patch = mpatches.Patch(color=(0.8, 0.2, 0.2), label='Negative Change')

    ax.legend(handles=[positive_patch, negative_patch], loc='lower right')

    plt.savefig(f"./images/{year}.png")
