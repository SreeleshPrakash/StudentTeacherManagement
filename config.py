DATABASE = {
    'host': 'localhost',
    'port': '5432',
    'database': 'student_teacher',
    'user': 'user',
    'password': 'password'
}


SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE['user']}:" \
    f"{DATABASE['password']}@" \
    f"{DATABASE['host']}:" \
    f"{DATABASE['port']}/{DATABASE['database']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
