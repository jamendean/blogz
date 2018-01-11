from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:avery2015@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'wordswordswords2018'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30))
    password = db.Column(db.String(16))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request   # run this function before calling request handler for incoming request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    print(session)
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    title_error = "Please fill in the title"
    content_error = "Pleae fill in the body"
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']
        if blog_title == '' and blog_content == '':
            return render_template('newpost.html', title_error=title_error, content_error=content_error)
        elif blog_title == '':
            return render_template('newpost.html', title_error=title_error, blog_content=blog_content)
        elif  blog_content == '':
            return render_template('newpost.html', content_error=content_error, blog_title=blog_title)
        else:
            email = session['email']
            owner = User.query.filter_by(email=email).first()
            new_post = Blog(blog_title, blog_content,owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id=' + str(new_post.id))
    
    return render_template('newpost.html')
    

@app.route('/blog', methods=['GET'])
def blog():
    blogs = Blog.query.all()
    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        blog_post = Blog.query.get(blog_id)
        new_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_entry.html', new_blog=blog_post)
    
    elif request.args.get('user'):
        user_email = request.args.get('user')
        user = User.query.filter_by(email=user_email).first()
        user_blogs = user.blogs
        return render_template('singleUser.html', blogs=user_blogs, user_email=user_email)
    
    return render_template('blog.html', blogs=blogs)
   

def is_valid_password(password):
    valid = False
    number = '0123456789'
    space = ' '
    # First character must be uppercase letter
    if password[0].isalpha() and password[0].isupper() and len(password) >= 6 and space not in password:
        i = 1
        while i < len(password):
            if password[i] in number:
                valid = True 
                return valid
            i += 1
    return valid
    
def is_valid_email(email):
    valid = False
    # Count number of '.' in email
    dot_count = email.count('.')
    space = ' '
    if dot_count == 1 and email.index('@') < email.index('.') and space not in email and email[0].isalpha():
        valid = True
        return valid 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        email_count = User.query.filter_by(email=email).count()
        if is_valid_email(email) and is_valid_password(password) and verify == password:
            if email_count == 0:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
            else:
                flash('Username already exists')
                return render_template('signup.html')
        elif email == '' and password == '' and verify == '':
            flash("Please verify that all required fileds are filled in")
            return render_template('signup.html')
        elif not is_valid_password(password):
            flash("Password needs to start with an uppercase letter, be at least 6 characters long, and contain at least one number")
            return render_template('signup.html')
        elif email == '' or password == '' or verify == '':
            flash("Please verify that all required fields are filled in")
            return render_template('signup.html')
        elif password != verify:
            flash('Password field and verify field do not match')
            return render_template('signup.html')
        elif not is_valid_email or not is_valid_password:
            flash('Invalid username or password')
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in", 'info')
            return redirect('/newpost')
        elif user and user.password != password:
            flash("Please enter correct password")
            return redirect('/login')
        elif not user:
            flash("Please verify that the username is correct. Username entered does not exist")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()