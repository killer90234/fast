from passlib.context import CryptContext

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

fake_db ={
    'james': {
        'username': 'james',
        'hashed_password' : pass_context.hash('123')
    }
}

def get_user(username: str):
    user = fake_db.get(username)
    return user

def verify_password(normal_pass: str, hashed_pass: str):
    return pass_context.verify(normal_pass, hashed_pass)