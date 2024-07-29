from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pr_url = db.Column(db.String(200), nullable=False)
    current_spec = db.Column(db.Text)
    proposed_spec = db.Column(db.Text)
    task_description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    emp_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    emp_id = request.args.get('empId')
    status = request.args.get('status')

    query = Task.query

    # Filter by emp_id if provided
    if emp_id:
        query = query.filter_by(emp_id=emp_id)

    # Filter by status if provided
    if status:
        query = query.filter_by(status=status)

    tasks = query.all()

    return jsonify({
        'tasks': [{
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'empId': task.emp_id
        } for task in tasks]
    })


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    if not data or not all(key in data for key in ('title', 'prUrl', 'empId')):
        return jsonify({'error': 'Missing required fields'}), 400

    new_task = Task(
        title=data['title'],
        pr_url=data['prUrl'],
        emp_id=data['empId'],
        current_spec=data.get('currentSpec', ''),
        proposed_spec=data.get('proposedSpec', ''),
        task_description=data.get('taskDescription', '')
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        'message': 'Task created successfully',
        'task': {
            'id': new_task.id,
            'title': new_task.title,
            'prUrl': new_task.pr_url,
            'empId': new_task.emp_id,
            'status': new_task.status
        }
    }), 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'id': task.id,
        'title': task.title,
        'prUrl': task.pr_url,
        'currentSpec': task.current_spec,
        'proposedSpec': task.proposed_spec,
        'taskDescription': task.task_description,
        'status': task.status,
        'empId': task.emp_id
    })


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json

    task.current_spec = data.get('currentSpec', task.current_spec)
    task.proposed_spec = data.get('proposedSpec', task.proposed_spec)
    task.task_description = data.get('taskDescription', task.task_description)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Task updated successfully'
    })


@app.route('/api/user', methods=['GET'])
def get_user():
    # 这里应该从cookie或session中获取用户信息
    # 为了演示，我们返回一个模拟的用户
    return jsonify({
        'name': 'Test User',
        'email': 'test@example.com',
        'empId': 'EMP001'
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)