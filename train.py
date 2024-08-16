import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV


from sklearn.metrics import mean_squared_error, r2_score

import joblib

data = pd.read_csv("train2.csv")
x = data.drop(columns = ["name", "fantasy_ppr", "rec_long", "rush_long", "rec_success"])
y = data["fantasy_ppr"]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=69)
scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

param_grid = {
    "n_estimators": [100,200,300],
    "max_features": ["sqrt", "log2"],
    "max_depth": [None, 10,20,30],
    "min_samples_split": [2,5,10],
    "min_samples_leaf": [1,2,4]
    }

model = RandomForestRegressor(n_estimators=200, random_state=69, max_depth=None, max_features="sqrt", min_samples_leaf=10) # Mean Squared Error: 3694.3224351622903 R-squared: 0.5532148178009912

model.fit(x_train, y_train)

joblib.dump(model, "fantasy_ppr_predictor.pkl")


y_pred = model.predict(x_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")
"""
{'max_depth': None, 'max_features': 'sqrt', 'min_samples_leaf': 4, 'min_samples_split': 10, 'n_estimators': 200}
"""
