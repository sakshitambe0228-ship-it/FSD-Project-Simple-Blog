from flask import Flask, request, render_template, redirect, abort
import psycopg2

app = Flask(__name__)


def db_connect():
    return psycopg2.connect(
        dbname="blog_db",
        user="postgres",
        password="sakshi",
        host="localhost",
        port="5432"
    )


def create_table():
    con = db_connect()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    con.commit()
    cur.close()
    con.close()

@app.route("/")
def home():
    con = db_connect()
    cur = con.cursor()

    cur.execute("SELECT id, title, created_at FROM posts ORDER BY id DESC")
    posts = cur.fetchall()

    cur.close()
    con.close()

    return render_template("index.html", posts=posts)

@app.route("/new", methods=["GET", "POST"])
def new():
    msg = ""

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if title == "" or content == "":
            msg = "Please fill in all fields."

        else:
            con = db_connect()
            cur = con.cursor()

            cur.execute(
                "INSERT INTO posts (title, content) VALUES (%s, %s)",
                (title, content)
            )

            con.commit()
            cur.close()
            con.close()

            return redirect("/")

    return render_template("new.html", msg=msg)

@app.route("/post/<int:id>")
def read(id):
    con = db_connect()
    cur = con.cursor()

    cur.execute(
        "SELECT id, title, content, created_at FROM posts WHERE id = %s",
        (id,)
    )
    post = cur.fetchone()

    cur.close()
    con.close()

    if post is None:
        abort(404)

    return render_template("post.html", post=post)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    con = db_connect()
    cur = con.cursor()

    cur.execute("DELETE FROM posts WHERE id = %s", (id,))

    con.commit()
    cur.close()
    con.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    msg = ""
    con = db_connect()
    cur = con.cursor()

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if title == "" or content == "":
            msg = "Please fill in all fields."

        else:
            cur.execute(
                "UPDATE posts SET title = %s, content = %s WHERE id = %s",
                (title, content, id)
            )
            con.commit()
            cur.close()
            con.close()
            return redirect("/post/" + str(id))

    cur.execute("SELECT id, title, content FROM posts WHERE id = %s", (id,))
    post = cur.fetchone()

    cur.close()
    con.close()

    if post is None:
        abort(404)

    return render_template("edit.html", post=post, msg=msg)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)