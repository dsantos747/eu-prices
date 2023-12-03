import pandas as pd
import matplotlib.pyplot as plt

food_raw = pd.read_csv("estat_prc_fsc_idx_en.csv")
food_categories = pd.read_csv("food_categories.csv", sep=";")

food_prices = food_raw[food_raw["indx"] == "HICP"]
food_prices = pd.merge(
    food_prices, food_categories, left_on="coicop", right_on="CODE", how="left"
)


def category_index_over_time(category: str, region: str, unit: str = "I15"):
    prices = food_prices[
        (food_prices["NAME"] == category)
        & (food_prices["unit"] == unit)
        & (food_prices["geo"] == region)
    ]
    return prices.sort_values(by="TIME_PERIOD")


cat1_prices = category_index_over_time("Beer", "PT")
cat2_prices = category_index_over_time("Beer", "ES")

cat1_cat2_prices = pd.merge(
    cat1_prices,
    cat2_prices,
    on="TIME_PERIOD",
    how="outer",
    suffixes=("_cat1", "_cat2"),
)

cat1_cat2_prices = cat1_cat2_prices.rename(
    columns={"OBS_VALUE_cat1": "PT", "OBS_VALUE_cat2": "ES"}
)

# print(cat1_prices.head(20))
# print(cat2_prices.head(20))

ax = cat1_cat2_prices.plot.line(x="TIME_PERIOD", y=["PT", "ES"])
ax.legend()
plt.show()
