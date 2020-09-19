import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success":True,
        "drinks": formatted_drinks
        })    

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
def drink_details(token):
    drinks = Drink.query.all()
    if not drinks:
        abort(404)

    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
        })    


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()   

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
            })
    except:
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

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(token, drink_id):
    required_drink = Drink.query.get(drink_id)
    if not required_drink:
        abort(404)
    #getting new updated drink
    data = request.get_json()

    new_title = data.get('title', None)
    new_recipe = data.get('recipe', None)

    try:
        #updating the old drink with the new drink data
        required_drink.title = new_title
        required_drink.recipe = json.dumps(new_recipe)
        
        required_drink.update()

        return jsonify({
            "success": True,
            "drinks": [required_drink.long()]
            })
    except:
        abort(422)
            


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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    required_drink = Drink.query.get(drink_id)
    if not required_drink:
        abort(404)
    try:
        required_drink_id = required_drink.id
        required_drink.delete()
        return jsonify({
            "success": True,
            "delete": required_drink_id
            })
    except:
        abort(422)        


## Error Handling
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



'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

    
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
        }), 400

@app.errorhandler(401)
def anauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def forrbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forrbidden"
    }), 403