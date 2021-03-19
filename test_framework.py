import pytest

from api import API
from middleware import Middleware


FILE_DIR = "css"
FILE_NAME = "main.css"
FILE_CONTENTS = "body {background-color: red}"


# helpers


def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)

    return asset


# tests


def test_basic_route_adding(api):
    @api.route("/home")
    def home(_, response):
        response.text("test")


def test_route_overlap_throws_exception(api):
    @api.route("/home")
    def home(_, response):
        response.text("test")

    with pytest.raises(AssertionError):
        @api.route("/home")
        def home(_, response):
            response.text("test")


def test_framework_test_client_can_send_requests(api, client):
    response_text = "It works"

    @api.route("/hey")
    def cool(_, response):
        response.text = response_text

    assert client.get("http://testserver/hey").text == response_text


def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(request, response, name):
        response.text = f"hey {name}"

    assert client.get("http://testserver/fred").text == "hey fred"
    assert client.get("http://testserver/boss").text == "hey boss"


def test_default_404_response(api, client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not found."


def test_class_based_handler_get(api, client):
    response_text = "GET request"

    @api.route("/book")
    class BookResource:
        def get(self, request, response):
            response.text = response_text

    assert client.get("http://testserver/book").text == response_text


def test_class_based_handler_post(api, client):
    response_text = "POST request"

    @api.route("/book")
    class BookResource:
        def post(self, request, response):
            response.text = response_text

    assert client.post("http://testserver/book").text == response_text


def test_class_based_not_allowed_method(api, client):
    response_text = "not used"

    @api.route("/book")
    class BookResource:
        def post(self, request, response):
            response.text = response_text

    with pytest.raises(AttributeError):
        client.get("http://testserver/book")


def test_alternative_route(api, client):
    response_text = "Alternative way"

    def home(_, response):
        response.text = response_text

    api.add_route("/alternative", home)
    assert client.get("http://testserver/alternative").text == response_text


def test_template(api, client):
    @api.route("/html")
    def html_handler(_, response):
        response.body = api.template("index.html", context={"title": "Some title", "name": "Some name"}).encode()

    response = client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Some title" in response.text
    assert "Some name" in response.text


def test_custom_exception_handler(api, client):
    def on_exception(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(on_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get("http://testserver/")

    assert response.text == "AttributeErrorHappened"


def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get("http://testserver/missing.css").status_code == 404


def test_assets_are_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)
    app = API(static_dir=str(static_dir))
    client = app.test_session()

    response = client.get(f"http://testserver/static/{FILE_DIR}/{FILE_NAME}")

    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_middleware_methods_are_called(api, client):
    process_request_called = False
    process_response_called = False

    class CallMiddlewareMethods(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, request):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, request, response):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CallMiddlewareMethods)

    @api.route('/')
    def index(request, response):
        response.text = "Yolo"

    client.get('http://testserver/')

    assert process_request_called is True
    assert process_response_called is True
