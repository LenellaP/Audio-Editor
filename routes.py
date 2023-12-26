from flask import Flask, render_template, Blueprint

from web_app.main import app

blueprint = Blueprint('blueprint', __name__, template_folder='templates')

@blueprint.route('/edit')
def edit():
    return render_template('edit.html')

app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(debug=True)