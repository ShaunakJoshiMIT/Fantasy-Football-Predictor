import csv

predictions = []
with open("predictions.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        predictions.append((row[0], row[-1]))

predictions.pop(0)
predictions.sort(key = lambda x: float(x[1]), reverse = True)
with open("sorted_predictions.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "prediction"])
    for name, prediction in predictions[1:]:
        writer.writerow([name, prediction])
