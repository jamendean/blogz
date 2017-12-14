from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:nemaj1990@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(240))

    def __init__(self, name, entry):
        self.name = name
        self.entry = entry 


@app.route('/blog')
def index():
    
    id_exists = request.args.get('id')
    if id_exists:
        single_blog = Blog.query.filter_by(id = id_exists).first()
        return render_template('singlepost.html', blog=single_blog)
    else:   
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        name = request.form['name']
        entry = request.form['entry']
        new_blog = Blog(name,entry)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog')

    else:
        return render_template('newpost.html')



if __name__ == '__main__':
    app.run()