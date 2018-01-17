from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:DaveG666@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['GET','POST'])
def new_post():
    return render_template('new_post.html', title="New Post")


@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_blog_entry = Blog(title,body)
        db.session.add(new_blog_entry)
        db.session.commit()
        

    blog = Blog.query.all()
    return render_template('blog.html', title="Blog list", blog=blog)
    
if __name__ == '__main__':
    app.run()