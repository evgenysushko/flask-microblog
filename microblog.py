from app import current_app, db, cli
from app.models import User, Post

app = current_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
