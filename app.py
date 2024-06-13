from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'mysecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='todos')

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return render_template("index.html")

@app.route('/notes', methods=['POST', 'GET'])
@login_required
def notes():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content, user_id=current_user.id)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/notes')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('notes.html', tasks=tasks, userid=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            return redirect('/')
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue registering the user'
    else:
        return render_template('register.html')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    
    if task_to_delete.user_id == current_user.id or current_user.username == 'admin':
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/notes')
        except:
            return 'There was a problem deleting that task'
    else:
        return '''
        <script>
            alert("You are not authorized to delete this task!");
            window.history.back();
        </script>
        '''

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)

    if current_user.username == task.user.username or current_user.username == 'admin':
        if request.method == 'POST':
            task.content = request.form['content']

            try:
                db.session.commit()
                return redirect('/notes')
            except:
                return 'There was an issue updating your task'

        else:
            return render_template('update.html', task=task)
    else:
        return '''
        <script>
            alert("You are not authorized to update this task!");
            window.history.back();
        </script>
        '''
    
@app.route('/admin_blog')
@login_required
def admin_blog():
    return render_template("admin_blog.html")

@app.route('/trainer')
@login_required
def trainer():
    return render_template("trainer.html")

@app.route('/contact')
@login_required
def contact():
    return render_template("contact.html")

@app.errorhandler(404)
def pagenotfound(e):
    return render_template("404.html"), 404

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)