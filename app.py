from flask import Flask, request, render_template
import pandas as pd
import datetime

app = Flask(__name__)

def validate(db_file, name, token):
    db_df = pd.read_csv(db_file)
    names = db_df['name'].values
    if name in names:
        db_token = db_df.loc[ db_df['name'] == name, 'token'].values[0]
        if db_token == token:
            return True
    return False

@app.route('/')
@app.route('/write')
@app.route('/read')
@app.route('/write/')
@app.route('/read/')
def index():
    return "No token."

@app.route("/write/<name>/<token>", methods=['GET'])
def write(name, token):
    if validate("write.csv", name, token):
        temperature = request.args.get('t')
        humidity    = request.args.get('h')
        if temperature and humidity:
            df  = pd.read_csv("data.csv")
            new = pd.DataFrame({'timestamp': [datetime.datetime.now().timestamp()], 'name': [name], 'temperature': [temperature], 'humidity': [humidity]})
            df = pd.concat([df, new])
            df.to_csv("data.csv", index=False)
            return f"Writen data {name}, {token}, {temperature}, {humidity}"
        return "No input data."
    return "False token."

@app.route("/read/<name>/<token>")
def read(name, token):
    if validate("read.csv", name, token):
        try:
            df = pd.read_csv("data.csv")
            return render_template("data.html", rows = df.iterrows() )
        except FileNotFoundError:
            return "data file not found"

if __name__ == "__main__":
    app.run(debug = True)
