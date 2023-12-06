import pandas as pd
import matplotlib.pyplot as plt

food_raw = pd.read_csv("eu_food_prices.csv")
food_categories = pd.read_csv("food_categories.csv", sep=";")
income_raw = pd.read_csv("ilc_di04.tsv", sep="\t|,", engine="python")

# Should re-write to process dataframe first, then apply filtering (eg. country, unit, hhtype) afterwards within a function

household_income = income_raw[
    (income_raw["geo\\time"] == "PT")
    & (income_raw["unit"] == "EUR")
    & (income_raw["indic_il"] == "MEI_E")
    & (income_raw["hhtyp"] == "TOTAL")
]

household_income = household_income.transpose()
household_income = household_income.iloc[4:].reset_index()
household_income.columns = ["Time", "Income"]
household_income["Income"] = pd.to_numeric(
    household_income["Income"].str.replace("b", "").str.strip(), errors="coerce"
)

household_income["Time"] = household_income["Time"].str.strip()
household_income["Time"] = pd.to_datetime(household_income["Time"], format="%Y")
household_income.sort_values(by="Time", inplace=True)
filled_years = pd.DataFrame(
    {
        "Time": pd.date_range(
            start=household_income["Time"].min(),
            end=household_income["Time"].max(),
            freq="Y",
        )
    }
)
parsed_income = pd.merge(
    filled_years,
    household_income,
    left_on=filled_years["Time"].dt.year,
    right_on=household_income["Time"].dt.year,
    how="left",
)
parsed_income = parsed_income.drop(columns=["key_0", "Time_y"])
parsed_income["Income"].fillna(
    parsed_income["Income"].interpolate(method="linear"), inplace=True
)


# Change the date to the first day of the year
parsed_income["Time_x"] = pd.to_datetime(parsed_income["Time_x"].dt.year, format="%Y")
parsed_income.columns = ["Time", "Income"]

food_prices = food_raw[food_raw["indx"] == "HICP"]
food_prices = pd.merge(
    food_prices, food_categories, left_on="coicop", right_on="CODE", how="left"
)


def category_index_over_time(category: str, region: str, unit: str = "I15"):
    prices = food_prices[
        (food_prices["NAME"] == category)
        & (food_prices["unit"] == unit)
        & (food_prices["geo"] == region)
    ].reset_index()

    result = prices.loc[:, ["TIME_PERIOD", "OBS_VALUE"]]
    result.columns = ["Time", "LPI"]

    result["Time"] = pd.to_datetime(
        result["Time"], format="%Y-%m"
    )  # .dt.to_period("M")
    # result["Time"] = result["Time"].astype(str)
    return result.sort_values(by="Time", ascending=True)


cat1_prices = category_index_over_time("Beer", "PT")
cat2_prices = category_index_over_time("Wine from grapes", "PT")

cat1_cat2_prices = pd.merge(
    cat1_prices,
    cat2_prices,
    on="Time",
    how="outer",
    suffixes=("_cat1", "_cat2"),
)

fig, ax = plt.subplots()
# fig.subplots_adjust(bottom=0.75)

twin1 = ax.twinx()

(p1,) = ax.plot(parsed_income["Time"], parsed_income["Income"], "C0", label="Income")

(p2,) = twin1.plot(
    cat1_cat2_prices["Time"], cat1_cat2_prices["LPI_cat1"], "C1", label="Beer"
)

(p3,) = twin1.plot(
    cat1_cat2_prices["Time"], cat1_cat2_prices["LPI_cat2"], "C2", label="Wine"
)

ax.set(xlabel="Year", ylabel="Mean Household Income")
twin1.set(ylabel="Laspeyres Price Index")

ax.yaxis.label.set_color(p1.get_color())
ax.tick_params(axis="y", colors=p1.get_color())

# twin1.yaxis.label.set_color(p2.get_color())
# twin1.tick_params(axis="y", colors=p2.get_color())

ax.legend(handles=[p1, p2, p3])

plt.show()
