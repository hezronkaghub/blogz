from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:abc123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'qscwdvefb'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index','login', 'sign_up','all_blogs','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    all_users = User.query.all()
    return render_template('index.html',all_users=all_users)


@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']

        if not username or not password or not verify_password or (len(username) < 3 or len(password) < 3):
            form_error = 'One or more fields are invalid'        
            return render_template('signup.html',form_error=form_error)
        
        if verify_password != password:
            password = ''
            verify_password = ''
            verify_error='Passwords do not match'
            return render_template('signup.html',verify_error=verify_error,username=username)
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            existing_user_error = 'Username already exists'
            return render_template('signup.html',existing_user_error=existing_user_error)
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if not user:
            password = ''
            username = ''
            username_error = 'Username does not exist'
            return render_template('login.html',username_error=username_error)
        
        elif user.password != password:
            password = ''
            username = ''
            password_error = 'Password is incorrect'
            return render_template('login.html', password_error=password_error)           
        
        else:
            session['username'] = username
            return redirect('/newpost')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        body_error = ''
        if not title or not body:
            if not title:
                title_error = 'Please add title'
            if not body:
                body_error = 'Please add post'
            return render_template('new_post.html',title_error=title_error,
                   body_error=body_error,title=title, body=body)    
        else:
            blog = Blog(title,body,owner)
            db.session.add(blog)
            db.session.commit()
            blog_id = Blog.query.get(blog.id)
            title = blog_id.title
            body = blog_id.body
            owner = session['username']
            owner_id = blog_id.owner_id
            return render_template('blog.html',title=title, body=body,owner=owner,owner_id=owner_id)
    else:
        return render_template('new_post.html')

@app.route('/blog', methods=['GET'])
def blog():
    if 'user' in request.args:
        blog_owner = Blog.query.get(request.args.get('user'))
        blog_by_user = Blog.query.filter_by(owner_id=blog_owner.id).all()
        if not blog_by_user:
            no_posts = 'No posts yet'
            return render_template('singleuser.html',no_posts=no_posts)
        return render_template('singleuser.html',blog_by_user=blog_by_user)
        
    if 'id' in request.args:
        blog = Blog.query.get(request.args.get('id'))
        title = blog.title
        body = blog.body
        blog_owner = User.query.filter_by(id=blog.owner_id).first()
        owner = blog_owner.username
        owner_id = blog_owner.id
        return render_template('blog.html',title=title,body=body,owner=owner,owner_id=owner_id)
    else:
        all_blogs = Blog.query.all()
        return render_template('all_blogs.html', title="All Blogs", all_blogs=all_blogs)

if __name__ == '__main__':
    app.run()
