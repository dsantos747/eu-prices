import pandas as pd
import matplotlib.pyplot as plt

food_raw = pd.read_csv("eu_food_prices.csv")
food_categories = pd.read_csv("food_categories.csv", sep=";")
income_raw = pd.read_csv("ilc_di04.tsv", sep="\t|,", engine="python")

household_income = income_raw[
    (income_raw["geo\\time"] == "PT")
    & (income_raw["unit"] == "EUR")
    & (income_raw["indic_il"] == "MEI_E")
    & (income_raw["hhtyp"] == "TOTAL")
]

household_income = household_income.transpose()
household_income = household_income.iloc[4:].reset_index()
household_income.columns = ["T", "Income"]
household_income["Income"] = (
    household_income["Income"]
    .str.replace("b", "")
    .str.strip()  # .str.replace(":", "0")
)
household_income["Income"] = pd.to_numeric(household_income["Income"], errors="coerce")
# household_income["Income"] = household_income["Income"].fillna(
#     pd.rolling_mean(household_income["Income"], 3, min_periods=1)
# )

household_income["T"] = household_income["T"].str.strip()
household_income["T"] = pd.to_datetime(household_income["T"], format="%Y")
household_income.sort_values(by="T", inplace=True)
filled_years = pd.DataFrame(
    {
        "T": pd.date_range(
            start=household_income["T"].min(), end=household_income["T"].max(), freq="Y"
        )
    }
)
parsed_income = pd.merge(
    filled_years,
    household_income,
    left_on=filled_years["T"].dt.year,
    right_on=household_income["T"].dt.year,
    how="left",
)
parsed_income["Income"].fillna(
    parsed_income["Income"].rolling(6, min_periods=1).mean(), inplace=True
)

parsed_income = parsed_income.drop(columns=["key_0", "T_y"])

# Change the date to the first day of the year
parsed_income["T_x"] = pd.to_datetime(parsed_income["T_x"].dt.year, format="%Y")
print(parsed_income.head(15))


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
    result.columns = ["T", "LPI"]

    result["T"] = pd.to_datetime(result["T"], format="%Y-%m")  # .dt.to_period("M")
    # result["T"] = result["T"].astype(str)
    return result.sort_values(by="T", ascending=True)


cat1_prices = category_index_over_time("Beer", "PT")
cat2_prices = category_index_over_time("Wine from grapes", "PT")

cat1_cat2_prices = pd.merge(
    cat1_prices,
    cat2_prices,
    on="T",
    how="outer",
    suffixes=("_cat1", "_cat2"),
)

income_prices = pd.merge(
    household_income, cat1_cat2_prices, on="T", how="outer"
).sort_values(by="T", ascending=True)

income_prices = income_prices.rename(
    columns={"Income": "Mean Household Income", "LPI_cat1": "Beer", "LPI_cat2": "Wine"}
)

income_prices.plot.line(
    x="T", y=["Mean Household Income", "Beer", "Wine"], secondary_y=["Beer", "Wine"]
)

# fig, ax1 = plt.subplots()

# income_prices.plot(
#     x="T",
#     y="Mean Household Income",
#     kind="bar",
#     color="blue",
#     alpha=0.2,
#     label="Mean Household Income",
#     width=12,
# )
# ax2 = ax1.twinx()
# income_prices.plot(
#     x="T",
#     y=["Beer", "Wine"],
#     kind="line",
#     secondary_y=True,
#     ax=ax2,
#     label=["Beer", "Wine"],
# )

# plt.show()
