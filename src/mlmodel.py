import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder

# read csv
#df = pd.read_csv('reed_dataset_for_yue.csv')
#df.head()

## connect data from postgresDB to 'df' ##

#keep only the columns needed for model
df = df[['categories', 'salary_min', 'salary_max', 'experience_level', 'skills']]
df = df.drop_duplicates()

# split for min salary - model 1
y1 = df['salary_min']
X1 = df.drop(['salary_min','salary_max'], axis=1)
X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, random_state=48)

# split for max salary - model 2
y2 = df['salary_max']
X2 = df.drop(['salary_min','salary_max'], axis=1)
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)


# Encoding
ohe = OneHotEncoder(drop = 'first', sparse=False)

# model 1 for min
cat1 = ['categories', 'experience_level']

X1_train[cat1] = ohe.fit_transform(X1_train[cat1])

X1_test[cat1] = ohe.transform(X1_test[cat1])

#encode 'skills'


# model 2 for max 
cat2 = ['categories', 'experience_level']

X2_train[cat2] = ohe.fit_transform(X2_train[cat2])

X2_test[cat2] = ohe.transform(X2_test[cat2])

# encode 'skills'

# model training and get predicted value
cl1 = RandomForestClassifier()
cl1.fit(X1_train, y1_train)
pred_y1 = cl1.predict(X1_test)

cl2 = RandomForestClassifier()
cl2.fit(X2_train, y2_train)
pred_y2 = cl2.predict(X2_test)
