from api import API
from middleware import Middleware

app = API(templates_dir='templates')


def custom_exception_handler(request, response, exception_cls):
    response.text = str(exception_cls)


app.add_exception_handler(custom_exception_handler)


# custom middleware


class SimpleCustomMiddleware(Middleware):
    def process_request(self, request):
        print("Processing request", request.url)

    def process_response(self, request, response):
        print("Processing response", request.url)


app.add_middleware(SimpleCustomMiddleware)


# routes


@app.route("/home")
def home(request, response):
    response.body = app.template(
        "index.html",
        context={"title": "Awesome Framework", "name": "Webby"}
    ).encode()


@app.route("/about")
def about(request, response):
    response.text = "Hello from the About page"


@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f'Hello, {name}!!'


@app.route("/sum/{num_1:d}/{num_2:d}")
def sum(request, response, num_1, num_2):
    total = int(num_1) + int(num_2)
    response.text = f'{num_1} + {num_2} = {total}'


@app.route("/book")
class BooksResource:
    def get(self, request, response):
        response.text = "Books page"

    def post(self, request, response):
        response.text = "Endpoint to create a book"


def handler(_, response):
    response.text = "sample"


app.add_route("/sample", handler)


@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be used.")


@app.route("/template")
def template_handler(req, resp):
    resp.html = app.template("index.html", context={"name": "Bumbo", "title": "Best Framework"})


@app.route("/json")
def json_handler(req, resp):
    resp.json = {"name": "data", "type": "JSON"}


@app.route("/text")
def text_handler(req, resp):
    resp.text = "This is a simple text"
