import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

model = joblib.load("fantasy_ppr_predictor.pkl")
data = pd.read_csv("averages.csv")
x_new = data.drop(columns = ["name", "rec_long", "rush_long", "rec_success"])


scaler = StandardScaler()

training_data = pd.read_csv("train2.csv")
x_train = training_data.drop(columns = ["name", "fantasy_ppr", "rec_long", "rush_long", "rec_success"])

scaler.fit(x_train)

x_new_scaled = scaler.transform(x_new)

predictions = model.predict(x_new_scaled)

data["predicted_fantasy_ppr"] = predictions

print(data[["name", "predicted_fantasy_ppr"]])

data.to_csv("predictions.csv", index = False)
