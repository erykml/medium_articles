import pandas as pd

df = pd.DataFrame(data={"id": ['a', 'b', 'c'],
                        "value": [1, 2, 3]})

def multiply_value(df, multiplier):
    df = df.copy()
    df["value"] = df["value"] * multiplier

multiplier_list = [1, 2, "3"]

for mult in multiplier_list:
    multiply_value(df, mult)

