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
        import traceback;
        traceback.print_exc()
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
    return render_template("index.html")


def get_strings_from_cols(rows):
    result = []

    for row in rows:
        result.append(f"{row[0]} {row[2]:<10} {row[3]:<15} {row[1][0:6]:<8} {row[4]}".replace(" ", "_"))

    return result


@app.route("/people")
def people():
    print(request.args)
    cursor = g.conn.execute("SELECT * FROM congressman")
    rows = []
    for result in cursor:
        row = []
        for field in result:
            row.append(field)  # can also be accessed using result[0]
        rows.append(row)
    cursor.close()

    row_strings = get_strings_from_cols(rows)
    final = [[] for i in range(len(row_strings))]
    for i in range(len(row_strings)):
        final[i].append(row_strings[i])
        final[i].append(row_strings[i][0])
    final2 = [final, "id Name__________________________State___________Branch___Party"]
    context = dict(data=final2)
    return render_template("people.html", **context)


def format_bill_rows(rows):
    result = []
    result.append("id_Name____________Passed_____Sponsor_______________________Description")
    result.append("-----------------------------------------------------------------------")
    for row in rows:
        result.append(f"{row[0]} {row[1]:<15} {row[2]:<10} {row[3]:<15} {row[4]}".replace(" ", "_"))

    return result


@app.route("/bills")
def bills():
    print(request.args)
    cursor = g.conn.execute("SELECT B.bid, B.name, B.passed, C.name AS sponsor, B.description "
                            + "FROM bill_sponsor_congress B LEFT OUTER JOIN congressman C ON B.cid = C.cid")
    rows = []
    for result in cursor:
        row = []
        for field in result:
            row.append(field)  # can also be accessed using result[0]
        rows.append(row)
    cursor.close()

    row_strings = format_bill_rows(rows)
    context = dict(data=row_strings)
    return render_template("bills.html", **context)


def format_committee_rows(rows):
    result = []
    result.append("Name_____________________________________Chair__________________________Description")
    result.append("-----------------------------------------------------------------------------------")

    for row in rows:
        result.append(f"{row[0]:<40} {row[1]:<10} {row[2]}".replace(" ", "_"))

    return result


@app.route("/committees")
def committees():
    print(request.args)
    cursor = g.conn.execute(
        "SELECT CT.name, C.name AS chair, CT.description FROM committee_chair CT LEFT OUTER JOIN congressman C ON C.cid=CT.cid ")
    rows = []
    for result in cursor:
        row = []
        for field in result:
            row.append(field)  # can also be accessed using result[0]
        rows.append(row)
    cursor.close()

    row_strings = format_committee_rows(rows)
    context = dict(data=row_strings)
    return render_template("committees.html", **context)


def format_individual_voting_record(rows):
    result = []
    result.append("id_Name___________Voted______Sponsored_______Description")
    result.append("--------------------------------------------------------")
    for row in rows:
        sponsored = ""
        if row[3]==0:
            sponsored = "no"
        else:
            sponsored = "yes"
        result.append(f"{row[0]} {row[1]:<15} {row[2]:<10} {sponsored:<15} {row[4]}".replace(" ", "_"))

    return result


@app.route("/individual")
def individual():
    print(request.args)
    query = "SELECT B.bid, B.name, V.decision AS vote, B.cid = V.cid AS Sponsored, B.description "\
            + f"FROM(SELECT * FROM votes WHERE cid = {request.args['cid']}) V " \
            + "LEFT OUTER JOIN bill_sponsor_congress B ON B.bid = V.bid"
    cursor = g.conn.execute(query)
    rows = []
    for result in cursor:
        row = []
        for field in result:
            row.append(field)  # can also be accessed using result[0]
        rows.append(row)

    cursor = g.conn.execute(f"SELECT name, description, cid FROM congressman WHERE cid = {request.args['cid']}")
    row = cursor.fetchone()
    name = row[0]
    description = row[1]
    cid = row[2]
    cursor.close()
    final = format_individual_voting_record(rows)
    context = dict(data=final, name=name, description=description, cid=cid)
    return render_template("individual.html", **context)


@app.route('/addNewIndividualDescription', methods=['POST'])
def add():
    new_description = request.form['description']
    cid = request.args['cid']
    g.conn.execute(f'UPDATE congressman SET description = \'{new_description}\' WHERE cid = {cid}')
    return redirect(f'/individual?cid={cid}')


def main():
    # app.run(host="0.0.0.0", port=8111, debug=False)
    app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()
