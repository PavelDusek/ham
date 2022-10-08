from flask import Flask, request, render_template
from pathlib import Path
import pandas as pd
import datetime

app = Flask(__name__)
variables = ["temperature", "humidity", "electricity", "water", "gas", "petrol", "car", "weight", "weight_muscle", "weight_fat", "weight_bone", "weight_water"]
for variable in variables:
    path = Path(f"{variable}.csv")
    if not path.is_file():
        df = pd.DataFrame(columns=["timestamp", "name", "value"])
        df.to_csv(f"{variable}.csv", index = False)

def validate(db_file, name, token, variable):
    db_df = pd.read_csv(db_file)
    names = db_df['name'].values
    if name in names:
        variables = db_df.loc[ db_df['name'] == name, 'variable'].values[0]
        variables = variables.split(",")
        db_token = db_df.loc[ db_df['name'] == name, 'token'].values[0]
        if (db_token == token and variable in variables):
            return True
    return False

@app.route('/')
@app.route('/input')
@app.route('/input/')
@app.route("/cam")
@app.route("/cam/")
def index():
    return "No token."

@app.route('/<variable>')
@app.route('/input/<variable>')
@app.route('/input/<variable>/')
def index2(variable):
    return "No token."

@app.route("/cam/<name>/<token>")
def cam(name, token):
    if not validate("read.csv", name, token, "cam"):
        return "False token."
    return render_template("camera.html")

@app.route("/input/<variable>/<name>/<token>", methods=['GET'])
def write(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate(db_file = "write.csv", name = name, token = token, variable = variable):
        return "False token."
    value = request.args.get('value')
    if not value:
        return "No input data."
    df = pd.read_csv(f"{variable}.csv")
    df = df.append({'timestamp': datetime.datetime.now().timestamp(), 'name': name, 'value': value}, ignore_index = True)
    print(df)
    df.to_csv(f"{variable}.csv", index=False)
    return f"Writen data {name}, {token}, {value} to {variable}.csv"

@app.route("/show/<variable>/<name>/<token>")
def show(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate(db_file = "read.csv", name = name, token = token, variable = variable):
        return "False token."
    df = pd.read_csv(f"{variable}.csv")

    #filter selected name
    name = request.args.get("name")
    if name:
        df = df.loc[ df['name'] == name ]

    #show only n rows
    n = request.args.get("n")
    if n:
        try:
            df = df.tail(int(n))
        except ValueError:
            return "n must be an integer"

    return render_template("show.html", rows = df.iterrows(), headers = df.columns)

@app.route("/dif/<variable>/<name>/<token>")
def dif(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate(db_file = "read.csv", name = name, token = token, variable = variable):
        return "False token."
    df = pd.read_csv(f"{variable}.csv")

    #filter selected name
    name = request.args.get("name")
    if name:
        df = df.loc[ df['name'] == name ]

    #Calculate difference between time points
    df['value'] = df['value'].diff()
    #Drop the starting points (filled with na)
    df.dropna(inplace = True)

    #show only n rows
    n = request.args.get("n")
    if n:
        try:
            df = df.tail(int(n))
        except ValueError:
            return "n must be an integer"

    return render_template("show.html", rows = df.iterrows(), headers = df.columns)

@app.route("/<variable>/<name>/<token>")
def read(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate(db_file = "read.csv", name = name, token = token, variable = variable):
        return "False token."
    df = pd.read_csv(f"{variable}.csv")

    #filter selected name
    name = request.args.get("name")
    if name:
        df = df.loc[ df['name'] == name ]

    #show only n rows
    n = request.args.get("n")
    if n:
        try:
            df = df.tail(int(n))
        except ValueError:
            return "n must be an integer"

    #convert timestamp to human readable dates
    df['timestamp'] = df['timestamp'].apply(lambda t: datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S.%f") )
    return render_template("data.html", rows = df.iterrows(), headers = df.columns)

if __name__ == "__main__":
    app.run(debug = True)
