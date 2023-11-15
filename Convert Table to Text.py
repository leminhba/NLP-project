import pandas as pd

# Tạo một DataFrame (bảng số liệu mẫu)
data = {
    "City": ["New York", "Los Angeles", "Chicago", "Houston"],
    "Population": [8398748, 3990456, 2705994, 2320268],
    "Area (sq. miles)": [468.9, 468.7, 227.3, 637.5],
    "State": ["New York", "California", "Illinois", "Texas"]
}

df = pd.DataFrame(data)


# Hàm để tạo lời mô tả và so sánh các cột
def describe_and_compare_columns(dataframe):
    column_descriptions = []
    for col in dataframe.columns:
        column_description = f"The '{col}' column contains values like: {', '.join(dataframe[col].astype(str).unique())}."
        column_descriptions.append(column_description)

    column_comparison = f"The columns can be compared in terms of their data distribution. For example, '{dataframe.columns[1]}' column has a population range from {dataframe[dataframe.columns[1]].min()} to {dataframe[dataframe.columns[1]].max()}, while '{dataframe.columns[2]}' column represents areas ranging from {dataframe[dataframe.columns[2]].min()} to {dataframe[dataframe.columns[2]].max()} square miles."

    return "\n".join(column_descriptions + [column_comparison])


# Tạo lời mô tả và so sánh các cột
column_description = describe_and_compare_columns(df)

# In lời mô tả và so sánh
print(column_description)