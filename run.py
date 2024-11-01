from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import SQLALCHEMY_DATABASE_URI
from models import db, User, StudentDetails, TeacherDetails, UserMapping, LoginLog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        # Check if email is already registered
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "Email already exists"}), 400

        # Create user
        user = User(
            name=data['name'],
            age=data['age'],
            category=data['category'],
            email=data['email']
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        # Assign details based on user category
        if user.category == 'student':
            student_details = StudentDetails(
                user_id=user.id,
                class_name=data['class'],
                division=data['division']
            )
            db.session.add(student_details)

        elif user.category == 'teacher':
            teacher_details = TeacherDetails(
                user_id=user.id,
                subject=data['subject']
            )
            db.session.add(teacher_details)

        db.session.commit()
        return jsonify({"message": "User created successfully", "user_id": user.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        # Retrieve user and validate password
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({"message": "Invalid email or password"}), 401

        # Log login
        login_log = LoginLog(
            user_id=user.id,
            name=user.name,
            category=user.category
        )
        db.session.add(login_log)
        db.session.commit()

        return jsonify({"message": "Login successful", "user_id": user.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# View All Users Endpoint
@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.filter_by(isdelete=False).all()
        response = [{"id": user.id, "name": user.name, "age": user.age} for user in users]
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# View User by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def view_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user or user.isdelete:
            return jsonify({"message": "User not found"}), 404

        response = {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "category": user.category,
            "created_on": user.created_on,
            "edited_on": user.edited_on
        }

        # Retrieve category-specific details
        if user.category == 'student':
            student_details = StudentDetails.query.filter_by(user_id=user.id).first()
            response['student_details'] = {"class": student_details.class_name, "division": student_details.division}
        elif user.category == 'teacher':
            teacher_details = TeacherDetails.query.filter_by(user_id=user.id).first()
            response['teacher_details'] = {"subject": teacher_details.subject}

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update User
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    try:
        user = User.query.get(user_id)
        if not user or user.isdelete:
            return jsonify({"message": "User not found"}), 404

        user.name = data.get('name', user.name)
        user.age = data.get('age', user.age)

        if user.category == 'student':
            student_details = StudentDetails.query.filter_by(user_id=user.id).first()
            student_details.class_name = data.get('class', student_details.class_name)
            student_details.division = data.get('division', student_details.division)

        elif user.category == 'teacher':
            teacher_details = TeacherDetails.query.filter_by(user_id=user.id).first()
            teacher_details.subject = data.get('subject', teacher_details.subject)

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Delete User
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user or user.isdelete:
            return jsonify({"message": "User not found"}), 404

        user.isdelete = True
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Map Student to Teacher
@app.route('/mapping', methods=['POST'])
def map_student_to_teacher():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')

    try:
        student = User.query.filter_by(id=student_id, category="student", isdelete=False).first()
        teacher = User.query.filter_by(id=teacher_id, category="teacher", isdelete=False).first()
        if not student or not teacher:
            return jsonify({"message": "Student or teacher not found"}), 404

        existing_mapping = UserMapping.query.filter_by(student_id=student_id, teacher_id=teacher_id, isdelete=False).first()
        if existing_mapping:
            return jsonify({"error": "Mapping already exists"}), 400

        mapping = UserMapping(student_id=student_id, teacher_id=teacher_id)
        db.session.add(mapping)
        db.session.commit()
        return jsonify({"message": "Student successfully mapped to teacher"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Login Logs
@app.route('/logs', methods=['GET'])
def get_login_logs():
    try:
        logs = LoginLog.query.all()
        response = [{"id": log.id, "user_id": log.user_id, "name": log.name, "category": log.category, "login_time": log.login_time} for log in logs]
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
