import unittest
from app.models import User, Role, Permission, AnonymousUser
from app import create_app, db

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_not_readable(self):
        user = User()
        user.password = 'somestring'
        with self.assertRaises(AttributeError):
            user.password

    def test_password_setter(self):
        user = User()
        user.password = 'something'
        self.assertTrue(user.password_hash is not None)

    def test_same_password_different_hashes(self):
        user = User()
        user.password = 'same'
        user2 = User()
        user2.password = 'same'
        self.assertTrue(user.password_hash != user2.password_hash)

    def test_password_verification(self):
        user = User()
        user.password = 'somelonglonglonglonglonglonglonglongstring'
        self.assertTrue(user.verify_password('somelonglonglonglonglonglonglonglongstring'))
        self.assertFalse(user.verify_password('notthesamestring'))

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(username = 'something', email='something@something.com', password='but')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.MODERATE))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
