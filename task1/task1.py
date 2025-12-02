import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

URL_BASE = "https://api-baltic.transparency-dashboard.eu/"
API_SINGLE = "api/v1/export"
# API_MULTIPLE = "api/v1/export-multiple" # Did not work due to how "," is formatted in the "requests" library.

os.makedirs("data_task1") # Data folder

# Helpder fucntion that 
def fetch_(url, api, params):
    r = requests.get(url+api,params)
    print("\nFetch code:",r.status_code,"")
    return r


# Loop through the list of ids to request using the single export API
ids = ["activations_afrr", "imbalance_volumes_v2"]
responses = []
for _id in ids:
    PARAMS = {
        "id": _id,
        "start_date": "2025-09-22T00:00",
        "end_date": "2025-09-23T00:00",
        "output_time_zone": "EET",
        "output_format": "json",
        "json_header_groups": "1"
    }

    r = fetch_(URL_BASE, API_SINGLE, PARAMS)
    obj = r.json()

    with open(f"data_task1/{_id}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

    responses.append(obj)

# Build the dataframes with the appropiate columns
dataframes = []
for obj in responses:
    data = obj["data"]
    columns = data["columns"]
    ts = data["timeseries"]

    # Build column names using grouping
    col_names = [f"{col['group_level_0']}_{col['label']}" for col in columns]

    rows = []
    for block in ts:
        row = {"timestamp": block["_from"]}

        # zip column names with values
        for name, value in zip(col_names, block["values"]):
            row[name] = value

        rows.append(row)

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(df)
    df = df.set_index("timestamp",drop=True)
    print(df)
    dataframes.append(df)


# Extract data for plotting, renaming the imbalance columns from the previous result.
afrr_data = dataframes[0]
imbalance_data = dataframes[1]
imbalance_data = imbalance_data.rename(columns={
                                       "Estonia_None" : "Estonia_imbalance",
                                       "Latvia_None" : "Latvia_imbalance",
                                       "Lithuania_None" : "Lithuania_imbalance"
                                        })


# Plot the results
fig, (ax_afrr, ax_v2) = plt.subplots(2, 1, figsize=(12, 8))

# aFRR plotting
styles_afrr = {
    "Estonia_Upward": "b-",
    "Estonia_Downward": "b--",
    "Latvia_Upward": "r-",
    "Latvia_Downward": "r--",
    "Lithuania_Upward": "g-",
    "Lithuania_Downward": "g--",
}
afrr_data.plot(
    title="aFRR",
    ylabel = "MW",
    legend=False,
    ax=ax_afrr,
    style=styles_afrr
)
ax_afrr.grid(True, which = "both", axis="both")
ax_afrr.legend(loc = "upper left",
                bbox_to_anchor = (0.85, 1.2),
                fontsize =  "small"
)

# imbalance plotting
styles_imbalance = {
    "Estonia_imbalance" : "b-",
    "Latvia_imbalance" : "r-",
    "Lithuania_imbalance" : "g-"
}
imbalance_data.plot(
    title="imbalance",
    ylabel = "MWh",
    legend=False,
    ax=ax_v2,
    style=styles_imbalance
)
ax_v2.grid(True, which = "both", axis="both")
ax_v2.legend()

# Cumulative data
print("\n")
print("Cumulative aFRR activations during the day [MW]:\n\n",afrr_data.sum())
print("\n")
print("Cumulative imbalance during the day [MWh]:\n\n",imbalance_data.sum())

plt.tight_layout(pad=2.0)
plt.show()