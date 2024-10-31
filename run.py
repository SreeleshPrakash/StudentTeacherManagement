# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI
from models import db, User, StudentDetails, TeacherDetails, UserMapping

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        user = User(name=data['name'], age=data['age'],
                    category=data['category'])
        db.session.add(user)
        db.session.commit()

        if user.category == 'student':
            student_details = StudentDetails(
                user_id=user.id, class_name=data['class'], division=data['division'])
            db.session.add(student_details)

        elif user.category == 'teacher':
            teacher_details = TeacherDetails(
                user_id=user.id, subject=data['subject'])
            db.session.add(teacher_details)

        db.session.commit()
        return jsonify({"message": "User created successfully", "id": user.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


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

        if user.category == 'student':
            student_details = StudentDetails.query.filter_by(
                user_id=user.id).first()
            response['student_details'] = {
                "class": student_details.class_name,
                "division": student_details.division
            }

        elif user.category == 'teacher':
            teacher_details = TeacherDetails.query.filter_by(
                user_id=user.id).first()
            response['teacher_details'] = {
                "subject": teacher_details.subject
            }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    data = request.json
    try:
        user = User.query.get(user_id)
        if not user or user.isdelete:
            return jsonify({"message": "User not found"}), 404

        user.name = data.get('name', user.name)
        user.age = data.get('age', user.age)
        req_category = data.get('category')

        if user.category != req_category:
            return jsonify({"message": "User category missmatch"}), 404

        if user.category == 'student':
            student_details = StudentDetails.query.filter_by(
                user_id=user.id).first()
            student_details.class_name = data.get(
                'class', student_details.class_name)
            student_details.division = data.get(
                'division', student_details.division)

        elif user.category == 'teacher':
            teacher_details = TeacherDetails.query.filter_by(
                user_id=user.id).first()
            teacher_details.subject = data.get(
                'subject', teacher_details.subject)

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user or user.isdelete:
            return jsonify({"message": "User not found"}), 404

        # Mark as deleted
        user.isdelete = True
        db.session.commit()

        mappings = UserMapping.query.filter(
            (UserMapping.student_id == user_id) | (
                UserMapping.teacher_id == user_id)
        ).all()

        # Set isdelete=True for each mapping
        for mapping in mappings:
            mapping.isdelete = True

        db.session.commit()

        return jsonify({"message": "User and associated mappings deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# =====================List Students by Teacher ID==============================

@app.route('/teachers/<int:teacher_id>/students', methods=['GET'])
def list_students_by_teacher(teacher_id):
    try:
        mappings = UserMapping.query.filter_by(
            teacher_id=teacher_id, isdelete=False).all()
        student_ids = [mapping.student_id for mapping in mappings]

        students = User.query.filter(User.id.in_(
            student_ids), User.isdelete == False).all()
        response = [{"id": student.id, "name": student.name,
                     "age": student.age} for student in students]

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ======================List Teachers by Student ID=============================

@app.route('/students/<int:student_id>/teachers', methods=['GET'])
def list_teachers_by_student(student_id):
    try:
        mappings = UserMapping.query.filter_by(
            student_id=student_id, isdelete=False).all()
        teacher_ids = [mapping.teacher_id for mapping in mappings]

        teachers = User.query.filter(User.id.in_(
            teacher_ids), User.isdelete == False).all()
        response = [{"id": teacher.id, "name": teacher.name,
                     "age": teacher.age} for teacher in teachers]

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ======================Users Mapping==========================================

# Map a student to a teacher
@app.route('/mapping', methods=['POST'])
def map_student_to_teacher():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')

    student = User.query.get(id=student_id, category="student")
    teacher = User.query.get(id=teacher_id, category="teacher")
    if not teacher or teacher.isdelete or not student or student.isdelete:
        return jsonify({"message": "User not found"}), 404

    # Check if mapping already exists
    existing_mapping = UserMapping.query.filter_by(
        student_id=student_id, teacher_id=teacher_id, isdelete=False).first()
    if existing_mapping:
        return jsonify({"error": "Mapping already exists for this student and teacher."}), 400

    new_mapping = UserMapping(student_id=student_id, teacher_id=teacher_id)
    db.session.add(new_mapping)
    db.session.commit()

    return jsonify({"message": "Student successfully mapped to teacher."}), 201


# Map multiple students to a teacher
@app.route('/mapping/bulk', methods=['POST'])
def map_multiple_students_to_teacher():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    student_ids = data.get('student_ids', [])

    teacher = User.query.get(id=teacher_id, category="teacher")
    if not teacher or teacher.isdelete:
        return jsonify({"message": "Teacher not found"}), 404

    user_notfound = []
    existing_mappings = []

    for student_id in student_ids:
        user = User.query.get(id=student_id, category="student")
        if not user or user.isdelete:
            user_notfound.append(student_id)

        # Check if mapping already exists
        if UserMapping.query.filter_by(student_id=student_id, teacher_id=teacher_id, isdelete=False).first():
            existing_mappings.append(student_id)

    if existing_mappings or user_notfound:
        return jsonify({
            "error": "Some mapping already exists / Some users not found",
            "existing_mappings": existing_mappings,
            "user_notfound": user_notfound
        }), 400

    # Mapp students with the teacher
    new_mappings = [
        UserMapping(student_id=student_id, teacher_id=teacher_id) for student_id in student_ids
    ]
    db.session.bulk_save_objects(new_mappings)
    db.session.commit()

    return jsonify({"message": "Students successfully mapped to teacher.", "mapped_students": student_ids}), 201


if __name__ == '__main__':
    app.run(debug=True)
