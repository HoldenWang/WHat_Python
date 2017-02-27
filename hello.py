import flask from Flask

@route("/")
def home():
	return '<h1>hello </h1>'
