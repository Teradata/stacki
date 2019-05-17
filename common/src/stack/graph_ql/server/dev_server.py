from flask import Flask
from flask_graphql import GraphQLView
from stack.graph_ql import schema
import os

view_func = GraphQLView.as_view("graphql", schema=schema, graphiql=True)
app = Flask(__name__)
app.add_url_rule("/", view_func=view_func)

def run():
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 8081))


if __name__ == "__main__": run()