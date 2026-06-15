from flask import Flask
from flask_cors import CORS
from routes.auth         import auth_bp
from routes.goals        import goals_bp
from routes.transactions import transactions_bp
from routes.percentages  import percentages_bp
from routes.insights     import insights_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp,         url_prefix="/api/auth")
app.register_blueprint(goals_bp,        url_prefix="/api/goals")
app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
app.register_blueprint(percentages_bp,  url_prefix="/api/percentages")
app.register_blueprint(insights_bp,     url_prefix="/api/insights")

if __name__ == "__main__":
    app.run(debug=True)