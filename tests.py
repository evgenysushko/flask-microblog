import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Post, User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class UserModelCase(unittest.TestCase):
    def setUp(self):
        # this will create the DB in memory
        # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # creates all DB tables in memory
        db.create_all()

    def tearDown(self):
        # removes the DB session, in case a test leaves session with some content inside
        db.session.remove()
        # deletes all the tables
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """Test for password hashing"""
        u = User(username="susan")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        """Test for avatar URL generation"""
        u = User(username="susan", email="susan@myexample.com")
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/"
                "1262715267516d85423208beaf4d6126"
                "?d=identicon&size=128"
            ),
        )

    def test_follow(self):
        """Test for following feature"""
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, "susan")
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, "john")

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        """Test for showing followed posts"""
        # create four users
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        u3 = User(username="mary", email="mary@example.com")
        u4 = User(username="david", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(
            body="post from john", author=u1, timestamp=now + timedelta(seconds=1)
        )
        p2 = Post(
            body="post from susan", author=u2, timestamp=now + timedelta(seconds=4)
        )
        p3 = Post(
            body="post from mary", author=u3, timestamp=now + timedelta(seconds=3)
        )
        p4 = Post(
            body="post from david", author=u4, timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
