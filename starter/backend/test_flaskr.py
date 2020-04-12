import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def testGetCategories(self):
        response = self.client().get('/categories')
        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.json['categories'], ["Science", "Art", "Geography", "History", "Entertainment", "Sports"])
        response = self.client().get('/category')
        self.assertTrue(response.status_code, 404)

    def testGetQuestions(self):
        response = self.client().get('/questions?page=2')
        self.assertTrue(response.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
