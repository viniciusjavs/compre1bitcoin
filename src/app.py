from buy1btc import buyFullBTC

from flask import Flask, render_template, jsonify
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html', btc=buyFullBTC())

@app.route("/api/btc")
def api():
    return jsonify(btc=buyFullBTC())

if __name__ == "__main__":
    app.run()
