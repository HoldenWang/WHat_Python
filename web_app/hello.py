import os
from flask.ext.migrate import Migrate, MigrateCommand
from flask import Flask ,make_response,redirect,render_template,session,redirect,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask import request
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from flask.ext.mail import Mail,Message
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=\
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLAlCHEMY_COMMIT_ON_TEARDOWN'] = True
#MAIL CONFIG
app.config['MAIL_SERVER'] =	'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_LTS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX']='[Flasky]'
app.config['FLASKY_MAIL_SENDER']='Flasky Admin <wagnhagnlll@163.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'hard to guess string'
manager=Manager(app)
bootstrap = Bootstrap(app)
moment=Moment(app)
migrate = Migrate(app,db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)

class NameForm(Form):
	name = StringField('What is your name?', validators=[Required()])
	submit = SubmitField('Submit')

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index= True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username

def make_shell_context():
	return dict(app=app,db=db,User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

def send_async_email(app, msg):
	with app.app_content():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.body = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr

@app.route('/', methods=['GET', 'POST'])
def index():
#    user_agent = request.headers.get('User-Agent')
#    return '<h1>your browser is %s~</h1>' % user_agent
#	name = None
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			session['known'] = False
			if app.config['FLASKY_ADMIN']:
				send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html', form=form, name=session.get('name'),
	known=session.get('known',False))

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
