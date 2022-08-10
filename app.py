from flask import Flask, request, render_template
from pathlib import Path
import pandas as pd
import datetime

app = Flask(__name__)
variables = ["temperature", "humidity", "electricity", "water", "gas", "petrol"]
for variable in variables:
    path = Path(f"{variable}.csv")
    if not path.is_file():
        df = pd.DataFrame(columns=["timestamp", "name", "value"])
        df.to_csv(f"{variable}.csv", index = False)

def validate(db_file, name, token):
    db_df = pd.read_csv(db_file)
    names = db_df['name'].values
    if name in names:
        db_token = db_df.loc[ db_df['name'] == name, 'token'].values[0]
        if db_token == token:
            return True
    return False

@app.route('/')
@app.route('/input')
@app.route('/input/')
def index():
    return "No token."

@app.route('/<variable>')
@app.route('/input/<variable>')
@app.route('/input/<variable>/')
def index2(variable):
    return "No token."

@app.route("/input/<variable>/<name>/<token>", methods=['GET'])
def write(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate("write.csv", name, token):
        return "False token."
    value = request.args.get('value')
    if not value:
        return "No input data."
    df = pd.read_csv(f"{variable}.csv")
    df = df.append({'timestamp': datetime.datetime.now().timestamp(), 'name': name, 'value': value}, ignore_index = True)
    print(df)
    df.to_csv(f"{variable}.csv", index=False)
    return f"Writen data {name}, {token}, {value} to {variable}.csv"

@app.route("/<variable>/<name>/<token>")
def read(variable, name, token):
    if not variable in variables:
        return "incorrect action"
    if not validate("read.csv", name, token):
        return "False token."
    df = pd.read_csv(f"{variable}.csv")
    return render_template("data.html", rows = df.iterrows(), headers = df.columns)

if __name__ == "__main__":
    app.run(debug = True)
