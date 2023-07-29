import pandas as pd

# load data
df = pd.read_excel('bio.xlsx')

# removing NA values from the
# dataframe df
df = df.fillna("")

# removing all the blank rows
df1 = df.dropna(how='all')

# picking the rows where present
# or absent values are there from
# 14 no column
df1 = df1[df1['Unnamed: 14'].str.contains('sent')]

# Extracting only the Employee
# Names
df_name = df.dropna(how='all')

# from column no 3 we are picking
# Employee names
df_name = df_name[df_name['Unnamed: 3'].str.contains('Employee')]

# creating a new dataframe for Status,
# Punch Records and Employee Codes
zippedList = list(
	zip(df1['Unnamed: 14'], df1['Unnamed: 15'], df_name['Unnamed: 7']))

abc = pd.DataFrame(zippedList)
abc.head()
