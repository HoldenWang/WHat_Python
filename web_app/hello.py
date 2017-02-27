from flask import Flask ,make_response,redirect,render_template
from flask_script import Manager 
from flask_bootstrap import Bootstrap
from flask import request
app = Flask(__name__)
manager=Manager(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
#    user_agent = request.headers.get('User-Agent')
#    return '<h1>your browser is %s~</h1>' % user_agent
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
#    return '<h1>Hello %s~</h1>' % name
    return render_template('user.html',name=name)

@app.route('/failure/')
def failed():
    return '<h1>bad request</h1>' ,400

@app.route('/cookie/')
def cooked():
    response = make_response('<h1>here is cookie by cooked</h1>')
    response.set_cookie('answer','42')
    return response

@app.route('/redirect')
def redirected():
    return redirect('http://www.jd.com')


@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user():
	abort(404)
    return '<h1>hi,%s</h1>' %user.name
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

if __name__=='__main__':
    manager.run()
