from datetime import datetime
from flask import Flask , request,render_template, redirect,session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError

    
import bcrypt
from flask import flash
import google.generativeai as genai
from flask import jsonify
import os
from dotenv import load_dotenv


# load environment variables from .env (if present)
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
# Use an environment variable for secret key in production
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change_me_in_production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(30), unique=True)
    # store only the hashed password (not unique, allow same password for multiple users)
    password=db.Column(db.String(128),nullable=False)
    Full_name=db.Column(db.String(30),nullable=False)
    # Use String for phone/number fields to allow leading zeros and flexible formats
    Number=db.Column(db.String(32),nullable=False)
    Phone_number=db.Column(db.String(32),nullable=False)
    Adhar_card_number=db.Column(db.String(64),nullable=False,unique=True)
    
    
    def __init__(self, username, email, password, Full_name, Number, Phone_number, Adhar_card_number):
        # assign provided values (do not access request inside model)
        self.username = username
        self.email = email
        # hash the password before saving
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.Full_name = Full_name
        self.Number = Number
        self.Phone_number = Phone_number
        self.Adhar_card_number = Adhar_card_number
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

        






class Fir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policeStation = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    fatherName = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phoneFax = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    distance = db.Column(db.String(100), nullable=False)
    direction = db.Column(db.String(100), nullable=False)
    nature = db.Column(db.String(200), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    particulars = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    witnesses= db.Column(db.Text)
    complaint = db.Column(db.Text, nullable=False)

    
    def __init__(self,policeStation,district,name,fatherName,address,phoneFax,email, distance,direction,nature,section,particulars,description,witnesses,complaint):
        self.policeStation= policeStation
        self.district =district
        self.name = name
        self.fatherName = fatherName
        self.address = address
        self.phoneFax = phoneFax
        self.email = email
        self.distance = distance
        self.direction = direction
        self.nature = nature
        self.section = section
        self.particulars = particulars
        self.description= description
        self.witnesses = witnesses
        self.complaint = complaint
        
        
    
class Visitor_ip(db.Model):
    __tablename__ = 'visitor_ip'  # Specify the table name explicitly if needed
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f'<Visitor {self.ip_address}>'

    
    


    
@app.route('/fir_form', methods=['GET', 'POST'])
def fir_form():
    if request.method == 'POST':
        # Extract data from the form
        policeStation = request.form.get('policeStation')
        district = request.form.get('district')
        name = request.form.get('name')
        fatherName = request.form.get('fatherName')
        address = request.form.get('address')
        phoneFax = request.form.get('phoneFax')
        email = request.form.get('email')
        distance = request.form.get('distance')
        direction = request.form.get('direction')
        nature = request.form.get('nature')
        section = request.form.get('section')
        particulars = request.form.get('particulars')
        description = request.form.get('description')
        witnesses = request.form.get('witnesses')
        complaint = request.form.get('complaint')
        print(name)
        
        new_fir = Fir(policeStation=policeStation,district=district,name=name,fatherName=fatherName,address=address,phoneFax=phoneFax,email=email, distance=distance,direction=direction,nature=nature,section=section,particulars=particulars,description=description,witnesses=witnesses,complaint=complaint)

        db.session.add(new_fir)
        db.session.commit()
        flash("your post has been submitted successfully", 'success')
        return redirect(url_for('bot'))

    return render_template('fir_form.html')


# Route to view FIR status
@app.route('/view_fir_status')
def view_fir_status():
    allfir = Fir.query.all()
    return render_template('view_fir_status.html',allfir=allfir)



@app.route('/sign_up' , methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        # handle request
        Full_name = request.form.get('Full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        Number = request.form.get('Number')
        Phone_number = request.form.get('Phone_number')
        Adhar_card_number = request.form.get('Adhar_card_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # basic validation
        if not (username and email and password and confirm_password):
            flash('Please fill in all required fields', 'error')
            return render_template('s.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('s.html')

        new_user = User(username=username, email=email, password=password, Full_name=Full_name, Number=Number, Phone_number=Phone_number, Adhar_card_number=Adhar_card_number)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except IntegrityError as e:
            db.session.rollback()
            # likely duplicate email or Adhar
            flash('A user with that email or Aadhar number already exists.', 'error')
            return render_template('s.html')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred creating the account.', 'error')
            return render_template('s.html')
        
    return render_template('s.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(username=username, email=email).first()

        if user and user.check_password(password):
            login_user(user)
            session['email'] = user.email
            session['username'] = user.username  # Save username in session
            return redirect(url_for('home_login'))
        else:
            return render_template('login.html',  error='Invalid credentials')

    return render_template('login.html')


@app.route('/index_bot', methods=['GET', 'POST'])
def bot():  
    return render_template('index_bot.html')



@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('sign_up'))
    return render_template('home.html')




 
@app.route('/home_login',)
def home_login():
    # capture IP (respect X-Forwarded-For if behind a proxy)
    xff = request.headers.get('X-Forwarded-For', None)
    remote_ip = (xff.split(',')[0].strip() if xff else request.remote_addr)
    try:
        visitor_ip = Visitor_ip(ip_address=remote_ip)
        db.session.add(visitor_ip)
        db.session.commit()
    except Exception:
        db.session.rollback()

    if 'email' in session:
        email = session['email']
        user = User.query.filter_by(email=email).first()
        return render_template('home_login.html', user=user)

    flash('YOU ARE NOT LOGGED IN', 'error')
    return redirect(url_for('home'))
   



@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        user = User.query.filter_by(email=email).first()
        return render_template('dashboard.html', user=user)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # log out via flask-login as well
    try:
        logout_user()
    except Exception:
        pass
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('home'))



def setup_gemini():
    # Read API key from environment (set GOOGLE_API_KEY in .env or the environment)
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Fail fast so developer knows to set the key
        raise RuntimeError('GOOGLE_API_KEY not set. Add it to a .env file or export it to the environment.')

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    return model

# Add this chat history
CHAT_HISTORY = [
    {"role": "user", "parts": ["""You are FIR-SAHAYAK, a helpful and empathetic FIR registration chatbot. Follow these rules:
    1. Always start with a warm greeting and introduce yourself
    2. Ask only ONE question at a time about the incident
    3. Wait for the user's response before asking the next question
    4. Show empathy and understanding in your responses
    5. Focus on gathering essential details systematically
    6. If the incident seems serious, recommend immediate police contact
    Base your next question on the user's previous response to maintain a natural conversation flow."""]},
    {"role": "model", "parts": ["""Welcome to FIR-SAHAYAK! I'm here to help you register your complaint and guide you through the process. I understand that reporting an incident can be stressful, and I'm here to make it as smooth as possible.

Could you please start by telling me what incident you'd like to report?"""]},
]

# Add these new routes to your app.py
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('userInput')
        if not user_input:
            return jsonify({'error': 'Invalid request body'}), 400

        model = setup_gemini()
        chat = model.start_chat(history=CHAT_HISTORY)
        response = chat.send_message(user_input)
        
        # Log the chat
        log_chat(user_input, response.text)
        
        return jsonify({'response': response.text})
    except Exception as e:
        print('Error in chat endpoint:', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

def log_chat(user_input, response):
    log_entry = f"{datetime.now().isoformat()}: User: {user_input}, Bot: {response}\n"
    with open('chat.txt', 'a') as f:
        f.write(log_entry)
        
        
        

with app.app_context():
    # create DB tables if they don't exist (safe on startup)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
    
    
    

