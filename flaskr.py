import os
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash

DATABASE = 'tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development_key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.route('/')
def show_entries():
  cur = g.db.execute('SELECT id, title, text FROM entries ORDER BY id DESC')
  entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
  return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
      [request.form['title'], request.form['text']])
  g.db.commit()
  flash('New entry was successfully posted')
  return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def delete_entry():
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('DELETE FROM entries WHERE id=?', [request.form['id']])
  g.db.commit()
  flash('Entry %d was successfully deleted', [request.form['id']])
  return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('show_entries'))

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('show_entries'))

if __name__ == '__main__':
  app.run(debug=True)
