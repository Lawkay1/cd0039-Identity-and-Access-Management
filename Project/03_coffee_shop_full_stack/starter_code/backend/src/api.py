import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''

db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():
    # print(request.headers)
    try:
        all_drink = Drink.query.all()
        for my_drinks in all_drink:
            drinks = [my_drinks.short()]

        return jsonify(
            {
                "success": True,
                "drinks": drinks
            }
        ), 200
    except Exception as e:
        print(e)
        abort(404)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    try:
        all_drink_details = Drink.query.all()

        for drink in all_drink_details:
            drinks = [drink.long()]

        return jsonify(
            {
                'success': True,
                'drinks': drinks
            }
        ), 200

    except Exception as e:
        abort(404)
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    recipe = json.dumps(request.json['recipe'])
    title = request.json['title']

    try:
        create_drink = Drink(recipe=recipe, title=title)
        create_drink.insert()
        new_drink = [create_drink.long()]
        return jsonify({
            "success": True,
            "drinks": new_drink
        }), 200
    except Exception as e:
        print(e)
        abort(422)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_details(payload, id):
    data = request.get_json()
    select_drink = Drink.query.filter(Drink.id == id).one_or_none()
    if select_drink:
        if 'title' in data:
            title = data.get('title')
            select_drink.title = title
        if 'recipe' in data:
            recipe = data.get('recipe')
            select_drink.recipe = json.dumps(recipe)
        select_drink.update()
        return jsonify({
            'success': True,
            'drinks': [select_drink.long()]
        })
    else:
        abort(404)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, id):
    drink = Drink.query.filter_by(id=id)
    if drink:
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': id
        })
    else:
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    '''Error handling for Bad Request'''
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    '''Error handling for Unauthorized Access'''
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401

@app.errorhandler(403)
def forbidden(error):
    '''Error handling for Authentication Error'''
    return jsonify({
        'success': False,
        'error': 403,
        'message:': 'Forbidden Authentication Error'
    }), 403

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "messages": "not-found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    }), error.status_code