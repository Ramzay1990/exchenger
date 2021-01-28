from flask import Flask, render_template
import requests


app = Flask(__name__)
app.debug = True


def exchange(corrency_to, amount):
    response = requests.get(f'https://api.exchangeratesapi.io/latest?symbols={corrency_to}')
    response_json = response.json()
    rates = response_json['rates']
    result = str(amount * rates[corrency_to])
    save_history(corrency_to, rates, amount, result)
    return result


def save_history(corrency_to, exchange_rate, amount, result):
    with open('history.txt', 'a') as f:
        f.write(f"{corrency_to},{exchange_rate[corrency_to]},{amount},{result}\n")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/eur_to_usd/<int:amount>/')
def eur_to_usd(amount):
    usd = exchange('USD', amount)
    return usd


@app.route('/eur_to_gbp/<int:amount>/')
def eur_to_gbp(amount):
    gbp = exchange('GBP', amount)
    return gbp


@app.route('/eur_to_php/<int:amount>/')
def eur_to_php(amount):
    php = exchange('PHP', amount)
    return php


@app.route('/history/')
def get_history():
    with open("history.txt")as f:
        history = f.readlines()
        return render_template("history.html", file=history)


if __name__ == '__main__':
    app.run()
