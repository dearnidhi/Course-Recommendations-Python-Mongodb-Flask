from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt
from datetime import datetime
from functions import is_logged_in,get_formatted_course_list

app = Flask(__name__)
app.secret_key = 'Welcome'

client = MongoClient("mongodb://localhost:27017/")
db = client["recommendation_system"]

users = db["users"]
users_survey_data = db['users_survey_data']
semester_details=db["semester_details"]



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if str(password) == str(confirm_password):                 
            password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            users.insert_one({'fullname': fullname,'email':email, 'password': hashed_password})
            return redirect(url_for('login'))
        elif str(password) != str(confirm_password):
            print("Passowrd not same")
            render_template('register.html')
            
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        user = users.find_one({'email': email})
        if user and bcrypt.checkpw(password, user['password']):
            session['email'] = email
            # Check if the user has completed the survey
            user_survey = users_survey_data.find_one({'user_email': email})
            if user_survey:
                # User has completed the survey, redirect to user profile
                return redirect(url_for('user_profile'))
            else:
                # User hasn't completed the survey, redirect to the survey page
                return redirect(url_for('survey'))
        else:
            message = "Wrong email or password. Please try again."

    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    if is_logged_in():
        session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            user = users.find_one({'email': email})
            if user:
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                users.update_one({'email': email}, {'$set': {'password': new_hashed_password}})
                return redirect(url_for('login'))
            else:
                print("User not found")
        else:
            print("Passwords do not match")

    return render_template('reset_password.html')


@app.route('/survey')
def survey():
    if is_logged_in():
        return render_template('survey.html')
    return redirect(url_for('login'))


@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    if is_logged_in():
        user_email = session['email']  # Get the user's email from the session
        data = request.form.to_dict()
        data['user_email'] = user_email  # Add the user's email to the survey data
        data['timestamp'] = datetime.now()  # Add a timestamp to track the submission time
        
        # Find the existing entry for the user
        existing_entry = users_survey_data.find_one({'user_email': user_email})
        
        if existing_entry:
            # If an entry exists, update it with the new data and keep the same ObjectID
            data['_id'] = existing_entry['_id']  # Retain the same ObjectID
            users_survey_data.replace_one({'_id': existing_entry['_id']}, data)  # Replace the existing entry with new data
        else:
            # If no entry exists, insert the new data
            users_survey_data.insert_one(data)
            
        return redirect(url_for('user_profile'))
    return redirect(url_for('login'))
    

@app.route('/user_profile')
def user_profile():
    if is_logged_in():
        # user_data = survey_collection.find_one()
        user_email = session['email']  # Get the user's email from the session
        user_data = users_survey_data.find_one({'user_email': user_email})  # Find all entries for the user
        # print(user_data)
        return render_template('user_profile.html', user_data=user_data)
    return redirect(url_for('login'))


@app.route('/recommendations', methods=['POST'])
def recommendations():
    if is_logged_in():
        # user_course_name = request.form.get('course_name', 'Software Engineering')
        user_semester = request.form.get('semester', 'Semester 1')
        email= session["email"]
        get_users_survey_data = users_survey_data.find_one({"user_email":email})
        print(get_users_survey_data)
        user_course_name = get_users_survey_data.get('codingInterests','Software Engineering')
        print(user_course_name)
        # print(user_semester)
        # Mongo query to retrieve semester details
        # query = {
        #     "$or": [
        #         {"course_name": user_course_name},
        #         {"course_name": "default"},
        #     ],
        #     "semester": {"$gte": user_semester}
        # }
        query ={
  "$or": [
    {
      "semester": {
        "$in": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 9", "Semester 10"]
      }
    },
    {
      "$and": [
        {
          "semester": {
            "$in": ["Semester 5", "Semester 6", "Semester 7", "Semester 8"]
          }
        },
        {
          "course_name": user_course_name
        }
      ]
    }
  ]
}

        print(query)

        results = semester_details.find(query)
        
        formatted_courses = get_formatted_course_list(course_data_from_mongo = results)
        print("************************************")
        print("formatted courses \n",formatted_courses)
        print("-------------------------------------")
        return render_template('recommendations.html',user_semester=user_semester,  courses=formatted_courses, user_course_name=user_course_name)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


