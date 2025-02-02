from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management
CORS(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    daily_points = db.Column(db.Integer, default=0)
    selected_actions = db.Column(db.Text, default='')

def get_or_create_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, daily_points=0, selected_actions='')
        db.session.add(user)
        db.session.commit()
    return user

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    session['username'] = username
    user = get_or_create_user(username)
    return jsonify({'message': 'User logged in', 'daily_points': user.daily_points, 'selected_actions': user.selected_actions})

@app.route('/submit_actions', methods=['POST'])
def submit_actions():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    data = request.json
    selected_actions = data.get('actions', [])
    daily_points = data.get('points', 0)
    
    user = User.query.filter_by(username=session['username']).first()
    if user:
        user.selected_actions = ','.join(selected_actions)
        user.daily_points = daily_points
        db.session.commit()
        return jsonify({'message': 'Actions saved', 'daily_points': user.daily_points})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'User logged out'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
