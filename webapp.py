from instagram import Instagram
from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
from flask import redirect
from flask import url_for
import functools
import base64
import io

app = Flask(__name__)
ig = Instagram()
ig.verify_instance()
ig.load_session()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if ig.is_auth() == False:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

@app.context_processor
def utility_processor():
    def b64e(t):
        tb = t.encode('ascii')
        b64b = base64.b64encode(tb)
        return b64b.decode('ascii')

    def b64d(b64t):
        b64b = b64t.encode('ascii')
        tb = base65.b64decode(b64b)
        return tb.decode('ascii')

    def posts_for_render(posts):
        def fill(n, p):
            for x in range(n):
                p.append({"is_fill":True})
        c=len(posts)
        i=0
        o=[]
        if c <= 3:
            fill(c - 3, posts)
            return [posts]
        while i < c:
            o.append(posts[i:i+3])
            i = i + 3
        last=o[len(o)-1]
        fill(3-len(last), last)
        return o

    return dict(b64e=b64e,b64d=b64d,posts_for_render=posts_for_render)

@app.route("/p/<string:code>")
@login_required
def view_post(code):
    ig.load_post(code)
    return render_template('post.html', post=ig.get_post())

@app.route("/<string:username>")
@login_required
def view_profile(username):
    ig.load_profile(username)
    if 'end_cursor' in request.args:
        ig.more_posts(request.args['end_cursor'])
    return render_template('profile.html', username=username, posts=ig.get_posts())

@app.route("/image")
def view_image():
    return send_file(
        io.BytesIO(ig.get_image(base64.b64decode(request.args['url']))),
        download_name='image.jpg',
        mimetype='image/jpg'
    )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            if ig.login(request.form['username'], request.form['password']):
                return 'Login Successful'
            else:
                if ig.in_chekpoint_mode:
                    return redirect(url_for('checkpoint'))
                else:
                    return 'Invalid Login'
        else:
            return 'Bad Request'

@app.route("/checkpoint", methods=['GET'])
def checkpoint():
    return render_template('checkpoint.html')

@app.route("/checkpoint/<int:mode>", methods=['GET', 'POST'])
def checkpoint_validate(mode):
    if request.method == 'GET':
        ig.login_challenge_start(mode)
        return render_template('checkpoint.html', mode=mode)
    if request.method == 'POST' and 'code' in request.form and ig.in_chekpoint_mode: 
        code = request.form['code']
        ig.login_challenge_validate(code)
        return 'Login Successful'
