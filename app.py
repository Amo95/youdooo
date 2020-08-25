from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # add flask modules
from flask_sqlalchemy import SQLAlchemy  # add flask_sqlalchemy module for database
from datetime import datetime
from flask_caching import Cache
import os

cache = Cache()
app = Flask(__name__)

location = os.path.abspath(os.getcwd()) + "/todo.db"
# flask_optimize = FlaskOptimize() # initialize optimizer

app.config['CACHE_TYPE'] = 'simple'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{location}' # add absolute path to db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # load modification in db
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)  # start sqlalchemy
cache.init_app(app)


class Task(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(80), nullable=False)
   created_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.now)

   def __repr__(self):
       return f'Todo : {self.name}'

# create endpoints
@app.route("/", methods=['POST', 'GET'])
# @flask_optimize.optimize()
@cache.cached(timeout=30)
def home():
  if request.method == "POST": # run this when request is post
    name = request.form['name']
    if len(name.strip()) == 0:
      flash("Enter Something!!")
    else:
      new_task = Task(name=name)
      db.session.add(new_task)
      db.session.commit()
    return redirect('/')
  else:
     tasks = Task.query.order_by(Task.created_at).all()  # order task by duration
  return render_template("home.html", tasks=tasks)  # render home.html 

@app.route('/delete/<int:id>')
# @flask_optimize.optimize()
@cache.cached(timeout=30)
def delete(id):
   task = Task.query.get_or_404(id)

   try:
       db.session.delete(task)
       db.session.commit()
       return redirect('/')
       # return jsonify({'result': 'success'})
   except Exception:
       return "There was a problem deleting data."

# update task
@app.route('/update/<int:id>', methods=['GET', 'POST'])
# @flask_optimize.optimize()
@cache.cached(timeout=30)
def update(id):
   task = Task.query.get_or_404(id)

   if request.method == 'POST':
       task.name = request.form['name']

       try:
           db.session.commit()
           return redirect('/')
       except:
           return "There was a problem updating data."

   else:
       title = "Update Task"
       return render_template('update.html', title=title, task=task)

@app.errorhandler(404)
# @flask_optimize.optimize()
@cache.cached(timeout=30)
def errror_404_page(error):
  return render_template("error.html")


if __name__ == "__main__":
   app.run(debug=True)

