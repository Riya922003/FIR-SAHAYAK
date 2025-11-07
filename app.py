from datetime import datetime
from flask import Flask , request,render_template, redirect,session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError, OperationalError

    
import bcrypt
from flask import flash
import google.generativeai as genai
from flask import jsonify
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv
import threading


# load environment variables from .env (if present)
load_dotenv()

# Read recaptcha keys (support old names for backward compatibility)
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY') or os.getenv('SITE_KEY')
RECAPTCHA_SECRET = os.getenv('RECAPTCHA_SECRET') or os.getenv('SECRET_KEY')

app = Flask(__name__)
# Read the database URL from the environment (e.g. DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# Prevent errors when the DB connection in the pool becomes invalid (network/SSL hiccups)
# This enables SQLAlchemy's pool_pre_ping which checks connections before use.
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = { 'pool_pre_ping': True }
db = SQLAlchemy(app)
# Use an environment variable for secret key in production
# Prefer SECRET_KEY, fall back to FLASK_SECRET_KEY for compatibility
app.secret_key = os.environ.get('SECRET_KEY', os.getenv('FLASK_SECRET_KEY', 'change_me_in_production'))

# --- Mail Configuration (Gmail example) ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# Optional default sender (helps some mail providers)
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))

# Instantiate Mail and serializer for generating timed tokens
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

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

    # --- Password reset token helpers ---
    def get_reset_token(self, expires_sec=1800):
        """Generates a secure, timed token. Default expiry argument is kept for API compatibility."""
        # serializer enforces expiry on loads (max_age); dumps does not take expiry
        return s.dumps(self.email, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token):
        """
        Verifies the reset token. Returns the User if valid, otherwise None.
        """
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=1800)
        except (SignatureExpired, BadTimeSignature):
            return None
        return User.query.filter_by(email=email).first()


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


class ChatLog(db.Model):
    __tablename__ = 'chat_log'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_input = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)

    def __init__(self, user_input, bot_response):
        self.user_input = user_input
        self.bot_response = bot_response

    
    


    
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
        # Accept either username or email-based login; prefer email if provided
        email = request.form.get('email')
        password = request.form.get('password')

        # Verify reCAPTCHA
        recaptcha_resp = request.form.get('g-recaptcha-response')
        recaptcha_secret = RECAPTCHA_SECRET
        if not recaptcha_resp or not recaptcha_secret:
            flash('Captcha validation failed. Please try again.', 'error')
            return render_template('login.html', error='Captcha required', recaptcha_site_key=RECAPTCHA_SITE_KEY)

        # Server-side verification with Google
        try:
            data = urllib.parse.urlencode({'secret': recaptcha_secret, 'response': recaptcha_resp}).encode()
            req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            print('Error verifying recaptcha:', e)
            flash('Captcha verification failed (network). Please try again.', 'error')
            return render_template('login.html', error='Captcha verification failed', recaptcha_site_key=RECAPTCHA_SITE_KEY)

        if not result.get('success'):
            flash('Captcha validation failed. Please try again.', 'error')
            return render_template('login.html', error='Invalid captcha', recaptcha_site_key=RECAPTCHA_SITE_KEY)

        # Find user by email (or username fallback)
        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        else:
            username = request.form.get('username')
            user = User.query.filter_by(username=username).first() if username else None

        if user and user.check_password(password):
            login_user(user)
            session['email'] = user.email
            session['username'] = user.username  # Save username in session
            return redirect(url_for('home_login'))
        else:
            return render_template('login.html',  error='Invalid credentials', recaptcha_site_key=RECAPTCHA_SITE_KEY)

    return render_template('login.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route('/index_bot', methods=['GET', 'POST'])
def bot():  
    return render_template('index_bot.html')


@app.route('/ajax_login', methods=['POST'])
def ajax_login():
    # AJAX login endpoint: returns JSON with success or error messages
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        recaptcha_resp = request.form.get('g-recaptcha-response')

        if not recaptcha_resp or not RECAPTCHA_SECRET:
            return jsonify({'success': False, 'error': 'Captcha required.'}), 400

        # Verify captcha with Google
        try:
            data = urllib.parse.urlencode({'secret': RECAPTCHA_SECRET, 'response': recaptcha_resp}).encode()
            req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            print('Error verifying recaptcha (ajax):', e)
            return jsonify({'success': False, 'error': 'Captcha verification failed (network).'}), 500

        if not result.get('success'):
            return jsonify({'success': False, 'error': 'Captcha validation failed.'}), 400

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        else:
            username = request.form.get('username')
            if username:
                user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            session['email'] = user.email
            session['username'] = user.username
            return jsonify({'success': True, 'redirect': url_for('home_login')}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials.'}), 401
    except Exception as e:
        print('Unexpected error in ajax_login:', e)
        return jsonify({'success': False, 'error': 'Internal server error.'}), 500


@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Validate a password-reset token and allow the user to set a new password.

    This route expects the token in the URL path and shows a form to enter a
    new password. On success, it updates the user's hashed password and
    redirects to the login page.
    """
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token. Please try again.', 'warning')
        return redirect(url_for('sign_up'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Please provide and confirm your new password.', 'danger')
            return render_template('reset_token.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_token.html', token=token)

        # Hash the new password and store it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_password
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error saving new password:', e)
            flash('An error occurred while updating the password. Please try again.', 'danger')
            return render_template('reset_token.html', token=token)

        flash('Your password has been successfully updated! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', token=token)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Request password-reset: collect email, send reset link if user exists.

    For security we always flash the same message so attackers cannot enumerate
    whether an email exists in the system.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('forgot_password.html')

        try:
            user = User.query.filter_by(email=email).first()
        except Exception as db_err:
            # Handle transient DB/SSL connection errors gracefully
            print('Database error during forgot_password:', repr(db_err))
            try:
                db.session.rollback()
            except Exception:
                pass
            flash('Database temporarily unavailable. Please try again in a few minutes.', 'danger')
            return render_template('forgot_password.html')
        if user:
            try:
                token = user.get_reset_token()
                reset_url = url_for('reset_token', token=token, _external=True)

                subject = 'FIR-SAHAYAK Password Reset'
                msg = Message(subject=subject, recipients=[user.email])
                # Plain text fallback
                msg.body = f"To reset your password, visit the following link:\n\n{reset_url}\n\nIf you did not request this, please ignore this email."
                # HTML body from template
                try:
                    msg.html = render_template('emails/reset_password.html', reset_url=reset_url, user=user)
                except Exception:
                    # If rendering fails, just continue with plain text
                    pass

                mail.send(msg)
            except Exception as e:
                print('Error sending password reset email:', e)
                # Do not reveal technical details to the user
                flash('There was an error sending the reset email. Please try again later.', 'danger')
                return render_template('forgot_password.html')

        # Always show generic message
        flash('If an account with that email exists, you will receive password reset instructions shortly.', 'info')
        return redirect(url_for('home'))

    return render_template('forgot_password.html')



@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('sign_up'))
    return render_template('home.html', recaptcha_site_key=os.getenv('SITE_KEY'))




 
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
        return render_template('home_login.html', user=user, recaptcha_site_key=os.getenv('SITE_KEY'))

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

def _save_chat_to_db(user_input, response):
    """Worker that runs inside an application context and writes the ChatLog record."""
    try:
        with app.app_context():
            new_log = ChatLog(user_input=user_input, bot_response=response)
            db.session.add(new_log)
            db.session.commit()
    except Exception as e:
        # Ensure we rollback on error and print to logs for debugging
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f"Error logging chat to database: {str(e)}")


def log_chat(user_input, response):
    """Start a background thread to save the chat log so the request isn't blocked.

    This function returns immediately after scheduling the write. Any DB errors
    are handled inside the worker and won't crash the request handler.
    """
    try:
        t = threading.Thread(target=_save_chat_to_db, args=(user_input, response), daemon=True)
        t.start()
    except Exception as e:
        # If the thread couldn't be started, print error but don't raise
        print(f"Failed to start background thread for chat logging: {str(e)}")
        
        
        

with app.app_context():
    # create DB tables if they don't exist (safe on startup)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
    
    
    

