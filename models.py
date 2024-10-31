from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)  # 'student' or 'teacher'
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    edited_on = db.Column(db.DateTime, onupdate=db.func.now())
    isdelete = db.Column(db.Boolean, default=False)

class StudentDetails(db.Model):
    __tablename__ = 'student_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    class_name = db.Column(db.String, nullable=False)
    division = db.Column(db.String, nullable=False)

class TeacherDetails(db.Model):
    __tablename__ = 'teacher_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    subject = db.Column(db.String, nullable=False)

class UserMapping(db.Model):
    __tablename__ = 'user_mapping'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    edited_on = db.Column(db.DateTime, onupdate=db.func.now())
    isdelete = db.Column(db.Boolean, default=False)
