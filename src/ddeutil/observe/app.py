import uvicorn
from fasthtml.common import Div, FastHTML, P

app = FastHTML()


@app.get("/")
def get():
    return Div(P("Hello World!"), hx_get="/change")


@app.get("/change")
def get():
    return P("Nice to be here!")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
