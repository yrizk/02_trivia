import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
from functools import reduce
import werkzeug
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  db = setup_db(app)

  cors = CORS(app, resources={r"/api/*" : {"origins": "*"}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
      return jsonify(categories=reduce(lambda x,y: x+y, Category.query.order_by('id').with_entities(Category.type).all()))

  @app.route('/questions')
  def get_questions():
      requested_pg = request.args.get("page", 1, type=int)
      results = Question.query.order_by('id').paginate(requested_pg, per_page=10,error_out=False).items
      return jsonify(
          page=requested_pg,
          questions=list(map(lambda i : i.format(), results)),
          total_questions = Question.query.count(),
          categories=Category.query.with_entities(Category.type).all(),
          current_category = results[0].category,
          count = Question.query.count()
      )

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    Question.query.filter_by(id=question_id).delete()
    db.session.commit()
    return jsonify(success=True)

  @app.route('/questions', methods=['POST'])
  def add_question():
    new_info = request.get_json()
    q = Question(
        question=new_info['question'],
        difficulty = new_info['difficulty'],
        answer=new_info['answer'],
        category = new_info['category']
    )
    db.session.add(q)
    db.session.commit()
    return jsonify(success=True)

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      search_term = request.get_json().get('searchTerm', '')
      query_results = Question.query.filter(func.lower(Question.question).contains(search_term.lower(), autoescape=True))
      return jsonify(questions=format(query_results))


  @app.route('/categories/<int:category_id>/questions')
  def get_questions_for_category(category_id):
      requested_pg = request.args.get("page", 1, type=int)
      results = Question.query.filter_by(category=category_id+1).order_by('id').paginate(requested_pg, per_page=10,error_out=False).items
      return jsonify(
          page=requested_pg,
          questions=format(results),
          count=len(results),
          current_category=Category.query.with_entities(Category.id, Category.type).filter_by(id=category_id+1).first(),
          categories=Category.query.with_entities(Category.id, Category.type).all()
      )

  def format(l):
      return list(map(lambda i : i.format(), l))

  @app.route('/quizzes', methods=['POST'])
  def quizzes():
      category_id = request.get_json()['quiz_category']['id']
# t  hese are just the ids.
      previous_questions = request.get_json()['previous_questions']
      q = Question.query.order_by('id').filter_by(category=int(category_id) + 1).filter(Question.id.notin_(previous_questions)).first()
      if q:
        q = q.format()
        previous_questions.append(q['id'])
      return jsonify(question=q,previous_questions=previous_questions)

  @app.errorhandler(404)
  def e_404(e):
      return 'The resource requested was not found'

  @app.errorhandler(422)
  def e_422(e):
      return 'Unable to process the requested resource'

  @app.errorhandler(werkzeug.exceptions.BadRequest)
  def generic_err_handler(e):
      return 'There was an error processing that request'

  return app


