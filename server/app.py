#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

# Initialize Flask app
app = Flask(__name__)

# Secret key for session management
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Compact JSON responses
app.json.compact = False

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Initialize Flask-Restful for API endpoints
api = Api(app)

# Resource for clearing session data
class ClearSession(Resource):

    def delete(self):
        # Reset session data
        session.pop('page_views', None)
        session.pop('user_id', None)
        return {}, 204

# Resource for retrieving all articles
class IndexArticle(Resource):
    
    def get(self):
        # Query all articles and convert to dictionary format
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

# Resource for showing a specific article
class ShowArticle(Resource):

    def get(self, id):
        # Initialize or increment page_views counter in session
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        # Check if page_views limit is reached
        if session['page_views'] <= 3:
            # Query article by id and convert to dictionary format
            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())
            return make_response(article_json, 200)
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

# Resource for user login
class Login(Resource):

    def post(self):
        # Get username from request JSON
        username = request.json.get('username')

        # Check if username is provided
        if not username:
            return {'message': 'Username not provided'}, 400

        # Query user by username
        user = User.query.filter_by(username=username).first()

        # Check if user exists
        if not user:
            return {'message': 'User not found'}, 404

        # Set user_id in session
        session['user_id'] = user.id

        # Return user data in JSON format
        return user.to_dict(), 200

# Resource for user logout
class Logout(Resource):

    def delete(self):
        # Remove user_id from session
        session.pop('user_id', None)
        return {}, 204

# Resource for checking session
class CheckSession(Resource):

    def get(self):
        # Get user_id from session
        user_id = session.get('user_id')

        # Check if user is logged in
        if user_id:
            # Query user by user_id and return user data in JSON format
            user = User.query.get(user_id)
            return user.to_dict(), 200
        else:
            # Return empty response with status code 401 if user is not logged in
            return {}, 401

# Add resources to API with corresponding endpoints
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
