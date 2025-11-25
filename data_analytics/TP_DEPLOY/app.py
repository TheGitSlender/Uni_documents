## We're building a basic Streamlit app for SOC Analysis

# Imports

import pandas as pd
import matplotlib.pyplot as plt 
from sklearn.preprocessing import StandardScaler
import seaborn

# Streamlit settings
import streamlit as st

st.set_page_config(page_title="SOC Analysis Tool", layout="wide")





# Let's extract the data
data = "data/cpu_load_data.csv"

df = pd.read_csv(data)
df = df.astype(float)

# We filtered the dataset already and know that there are no null values, is clean and all float.
# Let's Standardize the data now

scaler = StandardScaler()
df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

# The dataset is already quite simple and straightforward, we don't need PCA (independent features)
# After a feature selection study, it's best to use all of them for training.

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

X = df.drop(['cpu_load'], axis=1)
y = df['cpu_load']

x_train, x_test, y_train, y_test = train_test_split(X,y,test_size=0.1, random_state=15)

# Let's use a KNN for this