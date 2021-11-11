from forms import ExpressionForm
from config import Config
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response

app = Flask(__name__)
app.config.from_object(Config)


# DATABASEURI = "postgresql://fc2687:3840@104.196.152.219/proj1part2"
# engine = create_engine(DATABASEURI)


@app.route("/")
def index():
    return render_template('another.html')


def main():
    app.run(host="0.0.0.0", port=8111, debug=False)
    #app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()
