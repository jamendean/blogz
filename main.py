from flask import Flask, request, redirect
from flask import render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:nemaj1990@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # pylint: disable=locally-disabled, invalid-name
app.secret_key = 'sdfasdfasdf'


##### Classes ####
class Entry(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.String(50000))

    def __init__(self, name, text):
        self.name = name
        self.text = text


#### Routes ####
@app.route('/')
def to_mainpage():
    return redirect('/blog')


@app.route('/blog')
def blog():
    entries = Entry.query.all()
    return render_template('blog-home.html', title='Home', entries=entries)


@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        entry_name = request.form['name']
        entry_text = request.form['text']
        if entry_name == '' or entry_text == '':
            flash('Your blog post must have a title and body', 'error')
            return redirect('/newpost')
        else: 
            new_entry = Entry(entry_name, entry_text)
            db.session.add(new_entry)
            db.session.commit()
            entry_id = new_entry.id
            return redirect('/blog')
    return render_template('newpost.html')


@app.route('/view-post')
def view_post():
    entry_id = request.args.get('id')
    entry_veiw = Entry.query.filter_by(id=entry_id).first()
    name = entry_veiw.name
    text = entry_veiw.text
    return render_template('view-post.html', name=name, text=text)


if __name__ == '__main__':
    app.run()