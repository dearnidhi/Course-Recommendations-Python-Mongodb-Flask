from flask import Flask, render_template, request, redirect, url_for, session

def is_logged_in():
    return 'email' in session



def get_formatted_course_list(course_data_from_mongo):
    # Prepare the data
    results = course_data_from_mongo
    formatted_courses = []
    for course in results:
        print(course)
        formatted_course = {
            "semester": course['semester'],
            "course_name": course['course_name'],
            "mandatory_subjects": [],
            "choose_1_subjects": [],
            "choose_2_subjects": []
        }
        
        for i in range(5):
            mandatory_key = f'mandatory_{i}'
            choose_1_key = f'choose_1_{i}'
            choose_2_key = f'choose_2_{i}'
            
            if mandatory_key in str(course):
                formatted_course['mandatory_subjects'].append({
                    "subject_name": course[mandatory_key+'_subject_name'],
                    "course_code": course[mandatory_key+'_course_code'],
                    "description": course[mandatory_key+'_description'],
                    "course_link": course[mandatory_key+'_course_link']
                })
            if choose_1_key in str(course):
                formatted_course['choose_1_subjects'].append({
                    "subject_name": course[choose_1_key+'_subject_name'],
                    "course_code": course[choose_1_key+'_course_code'],
                    "description": course[choose_1_key+'_description'],
                    "course_link": course[choose_1_key+'_course_link']
                })
            
            if choose_2_key in str(course):
                formatted_course['choose_2_subjects'].append({
                    "subject_name": course[choose_2_key+'_subject_name'],
                    "course_code": course[choose_2_key+'_course_code'],
                    "description": course[choose_2_key+'_description'],
                    "course_link": course[choose_2_key+'_course_link']
                })
        
        formatted_courses.append(formatted_course)
    return formatted_courses