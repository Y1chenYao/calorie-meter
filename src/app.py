import json

from db import db
from flask import Flask
from flask import request
from db import Course
from db import User
from db import Assignment


# define db filename
app = Flask(__name__)
db_filename = "cms.db"

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    # create all tables
    db.create_all()


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# ROUTES
# ------------------------------------------------------

@app.route("/")
@app.route("/api/courses/")
def get_courses():
    # Endpoint for getting all courses
    return success_response({"courses": [t.serialize() for t in Course.query.all()]})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    # Endpoint for creating a new course
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")
    if code is None or name is None:
        return failure_response("Bad request", 400)
    new_course = Course(code=code, name=name)
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course_by_id(course_id):
    # Endpoint for getting a course by id
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course_by_id(course_id):
    # Endpoint for deleting a course by id
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/users/", methods=["POST"])
def create_user():
    # Endpoint for creating a new user
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")
    print(netid)
    if name is None or netid is None:
        return failure_response("Bad request", 400)
    new_user = User(name=name, netid=netid)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    # Endpoint for getting a user by id
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    # Endpiont to assign an instructor/user to a course by course

    # Validate course
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    # Validate body
    body = json.loads(request.data)
    user_id = body.get("user_id")
    type = body.get("type")
    if user_id is None or type is None:
        return failure_response("Bad request", 400)
    # Validate user
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    # Add relation to assoc table
    if type == "student":
        course.students.append(user)
        db.session.commit()
        return success_response(course.serialize())
    elif type == "instructor":
        course.instructors.append(user)
        db.session.commit()
        return success_response(course.serialize())
    else:
        return failure_response("Bad request", 400)


@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def add_assignment_to_course(course_id):
    # Endpoint for adding an assignment to a course
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")
    if title is None or due_date is None:
        return failure_response("Bad request", 400)
    new_assignment = Assignment(
        title=title, due_date=due_date, course_id=course_id)
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


if __name__ == "__main__":
    # I don't know why but 0.0.0.0 doesn't work on my windows PC
    app.run(host="0.0.0.0", port=5000, debug=True)
