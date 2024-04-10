import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# read csv
df = pd.read_csv('reed_dataset_for_yue.csv')
df.head()

#keep only the columns needed for model
df = df[['jobCategory', 'minimumsalary_yearly', 'maximumsalary_yearly', 'jobLevel', 'jobSkills', 'jobSite']]
df = df.drop_duplicates()

## change headers ##
# df.columns = []


# split, model_1 for min salary 
y = df['minimumsalary_yearly']
X = df.drop('minimumsalary_yearly', axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=48)

# Encoding
le = LabelEncoder()

X_train['jobCategory'] = le.fit_transform(X_train['jobCategory'])
X_test['jobCategory'] = le.transform(X_test['jobCategory'])

X_train['jobLevel'] = le.fit_transform(X_train['jobLevel'])
X_test['jobLevel'] = le.transform(X_test['jobLevel'])

X_train['jobSkills'] = le.fit_transform(X_train['jobSkills'])
X_test['jobSkills'] = le.transform(X_test['jobSkills'])

X_train['jobSite'] = le.fit_transform(X_train['jobSite'])
X_test['jobSite'] = le.transform(X_test['jobSite'])