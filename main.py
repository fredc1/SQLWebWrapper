from config import Config
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import os
from flask import Flask, flash, request, render_template, g, redirect, Response

app = Flask(__name__)
app.config.from_object(Config)


DATABASEURI = "postgresql://fc2687:3840@35.196.73.133/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route("/")
def index():
    print(request.args)
    cursor = g.conn.execute("SELECT cid FROM senator")
    names = []
    for result in cursor:
        names.append(result['cid'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)
    return render_template("index.html", **context)


def main():
    app.run(host="0.0.0.0", port=8111, debug=False)
    #app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()
