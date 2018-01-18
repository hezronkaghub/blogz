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


@app.route('/newpost', methods=['GET'])
def new_post():
    return render_template('new_post.html')


@app.route('/newpost', methods=['POST'])
def verify_post():
    title = request.form['title']
    body = request.form['body']
    title_error = ''
    body_error = ''
    if not title or not body:
        if not title:
            title_error = 'Please add title'
        if not body:
            body_error = 'Please add post'
        return render_template('new_post.html',title_error=title_error, body_error=body_error,title=title, body=body)    
    else:
        new_blog_entry = Blog(title,body)
        db.session.add(new_blog_entry)
        db.session.commit()
        blog_id = new_blog_entry.id
        one_blog = Blog.query.get(blog_id)
        title = one_blog.title
        body = one_blog.body

        return render_template('one_blog.html',title=title, body=body)
        

@app.route('/blog', methods=['POST','GET'])
def blog():
    blog = Blog.query.all()
    return render_template('blog.html', title="Blog list", blog=blog)
    
@app.route('/one_blog', methods=['GET'])
def one_blog():
    blog_id = request.args.get('id')
    one_blog = Blog.query.get(blog_id)
    title = one_blog.title
    body = one_blog.body
    return render_template('one_blog.html',title=title, body=body)
       

if __name__ == '__main__':
    app.run()