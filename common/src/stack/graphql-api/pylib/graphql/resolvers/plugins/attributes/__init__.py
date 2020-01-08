from stack.graphql.utils import dynamic_import


# Dynamically import the plugins in this folder
dynamic_import(__file__, __name__)
