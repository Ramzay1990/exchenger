from flask import Flask, render_template, g
import requests
import sqlite3


app = Flask(__name__)
app.debug = True


DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        db = g._database = conn
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def exchange(currency_to, amount):
    response = requests.get(f'https://api.exchangeratesapi.io/latest?symbols={currency_to}')
    response_json = response.json()
    rates = response_json['rates']
    result = str(amount * rates[currency_to])
    rates = rates[currency_to]
    save_history_to_database(currency_to, rates, amount, result)
    return result


def save_history_to_database(*args):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
            insert into exchange(currency_to, rates, amount, 'result')
                values(?, ?, ?, ?)
        """, args)
    conn.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/eur_to_usd/<int:amount>/')
def eur_to_usd(amount):
    usd = exchange('USD', amount)
    return f"Из 1 EURO вы получите {usd} долларов США!"


@app.route('/eur_to_gbp/<int:amount>/')
def eur_to_gbp(amount):
    gbp = exchange('GBP', amount)
    return f" Из 1 EURO вы получите {gbp} фунтов стерлингов!"


@app.route('/eur_to_php/<int:amount>/')
def eur_to_php(amount):
    php = exchange('PHP', amount)
    return f" Из 1 EURO вы получите {php} филиппинских песо!"


@app.route("/history/")
def get_history():
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                    select currency_to, rates, amount, result
                    from exchange
                    where 1
                """)
    return render_template('history.html', history=resp.fetchall(), static=1)


@app.route("/history/statistics/")
def statistic():
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                  select currency_to,sum(result) as sum_result, count(currency_to) as count_res
                    from exchange GROUP BY currency_to;
                """)
    return render_template('history.html', history=resp.fetchall(), static=0)


@app.route('/history/currency/<to_currency>/')
def history_currency(to_currency):
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                select currency_to, rates,amount,result
                from exchange
                where currency_to = ?
            """, (to_currency, ))
    return render_template('history.html', history=resp.fetchall(), static=1)


@app.route('/history/amount_gte/<number>/')
def amount_gte(number):
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                select currency_to, rates,amount,result
                from exchange
                where amount >= ?
            """, (number, ))
    return render_template('history.html', history=resp.fetchall(), static=1)


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    # init_db()
    app.run()
