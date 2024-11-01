from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)  # 'student' or 'teacher'
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    edited_on = db.Column(db.DateTime, onupdate=db.func.now())
    isdelete = db.Column(db.Boolean, default=False, index=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class StudentDetails(db.Model):
    __tablename__ = 'student_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), unique=True)
    class_name = db.Column(db.String, nullable=False)
    division = db.Column(db.String, nullable=False)

class TeacherDetails(db.Model):
    __tablename__ = 'teacher_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), unique=True)
    subject = db.Column(db.String, nullable=False)

class UserMapping(db.Model):
    __tablename__ = 'user_mapping'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    edited_on = db.Column(db.DateTime, onupdate=db.func.now())
    isdelete = db.Column(db.Boolean, default=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'teacher_id', name='unique_student_teacher'),)


class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    login_time = db.Column(db.DateTime, server_default=db.func.now())
