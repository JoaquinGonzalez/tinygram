from instagram import Instagram
from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
import base64
import io

app = Flask(__name__)

ig = Instagram('<username>', '<password>')
ig.verify_instance()
ig.login()

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
        c=len(posts)
        i=0
        o=[]
        if c <= 3:
            return [posts]
        while i < c:
            o.append(posts[i:i+3])
            i = i + 3
        return o

    return dict(b64e=b64e,b64d=b64d,posts_for_render=posts_for_render)

@app.route("/post/<string:code>")
def view_post(code):
    ig.load_post(code)
    return render_template('post.html', post=ig.get_post())

@app.route("/<string:username>")
def view_profile(username):
    ig.load_profile(username)
    return render_template('profile.html', posts=ig.get_posts())

@app.route("/image")
def view_image():
    return send_file(
        io.BytesIO(ig.get_image(base64.b64decode(request.args['url']))),
        download_name='image.jpg',
        mimetype='image/jpg'
    )

