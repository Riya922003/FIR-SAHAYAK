from flask import Flask , request,render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(30), unique=True)
    confirm_password=db.Column(db.String(10),nullable=False,unique=True)
    password=db.Column(db.String(10),nullable=False,unique=True)
    Full_name=db.Column(db.String(30),nullable=False)
    Number=db.Column(db.Integer,nullable=False)
    Phone_number=db.Column(db.Integer,nullable=False)
    Adhar_card_number=db.Column(db.Integer,nullable=False,unique=True)
    
    
    def __init__(self,email,password,username,Full_name,Number,Phone_number,Adhar_card_number,confirm_password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        self.Full_name = request.form['Full_name']
        self.Number = Number
        self.Phone_number = Phone_number
        self.Adhar_card_number = Adhar_card_number
        self.confirm_password = confirm_password
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()
    

@app.route('/')
def home():
    if request.method == 'POST':
        return redirect('/sign_up')
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(username=username, email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            session['username'] = user.username  # Save username in session
            return redirect('/home_login')
        else:
            return render_template('login.html',  error='Invalid credentials')

    return render_template('login.html')


@app.route('/index_bot', methods=['GET', 'POST'])
def bot():  
    return render_template('index_bot.html')

 
@app.route('/home_login',)
def home_login():  
    if 'email' in session:
        email = session['email']
        username = session['username']
        user = User.query.filter_by(email=email).first()
        return render_template('/home_login.html', user=user)
    

    
@app.route('/sign_up' , methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        # handle request
        Full_name = request.form['Full_name']
        username = request.form['username']
        email = request.form['email']
        Number = request.form['Number']
        Phone_number = request.form['Phone_number']
        Adhar_card_number = request.form['Adhar_card_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        new_user = User(Full_name=Full_name,username=username,email=email,Number=Number,Phone_number=Phone_number,Adhar_card_number=Adhar_card_number,password=password,confirm_password=confirm_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
        
    return render_template('s.html')


@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        username = session['username']
        user = User.query.filter_by(email=email).first()
        return render_template('dashboard.html', user=user)
    
    
@app.route('/view_fir_status')
def view_fir_status():
    try:
        with open('chat.txt', 'r') as file:
            chat_log = file.read()
    except FileNotFoundError:
        chat_log = 'Chat log not found'
    
    if 'email' in session:
        email = session['email']
        username = session['username']
        user = User.query.filter_by(email=email).first()
        return render_template('view_fir_status.html', user=user, chat_log=chat_log)



    

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

if __name__=='__main__':
   
    app.run(debug=True)