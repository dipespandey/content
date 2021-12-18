from sqlalchemy.orm.session import Session
from .database import create_connection, StudyProgram

program_queries_possible = [
    'deadline', 'deadlines', 'city', 'more info', 'more_info', 'more information', 'courses',
    'links', 'duration', 'language_taught', 'language taught', 'languages', 'language', 
    'requirements', 'grades_required', 'grades', 'grade', 'grades required'
]

def intro_response():
    response = "\nHello, I am a chatbot built for NTNU." +\
    "you can ask me general questions like: " +\
    "\nWhat can you do? " +\
    "\nWhat courses are available in NTNU?"
    return response


def get_all_courses():
    session: Session = create_connection()
    all_programs = session.query(StudyProgram).all()
    
    response = "I found the following results:\n" + \
    "\n".join([f"{i.entry_id} -> {i.coursecode}: {i.title}" for i in all_programs]) + \
    "\n\nPlease pick the numeric code to know more about the course"
    
    session.close()
    return response


def get_course_by_id(id):
    session: Session = create_connection()
    course = session.query(StudyProgram).filter(StudyProgram.entry_id==id).first()
    if not course:
        response = f"Sorry, course with code {id} was not found!"
    else:
        response = f"You selected {id}:\n" +\
            f"{course.coursecode} -> {course.title}\n" +\
            f"You can ask specifics about this course like: \
                \ncourses, deadline, city, languages, links, requirements, grades\
                \nYou can ask me for other courses when you are done checking {course.coursecode}."

    session.close()
    return response


def get_course_object_by_id(id):
    session: Session = create_connection()
    course_obj = session.query(StudyProgram).filter(StudyProgram.entry_id==id).first()
    session.close()
    return course_obj


def get_course_by_coursecode(code):
    session: Session = create_connection()
    course_obj = session.query(StudyProgram).filter(StudyProgram.coursecode==code).first()
    session.close()
    return course_obj
    

def get_study_programs_by_query(filtertype, filtervalue):
    session: Session = create_connection()
    if filtertype=='city':
        courses = session.query(StudyProgram).filter(StudyProgram.city==filtervalue).all()
    elif filtertype=='language':
        courses = session.query(StudyProgram).filter(StudyProgram.language_taught==filtervalue).all()
    if filtertype=='duration':
        courses = session.query(StudyProgram).filter(StudyProgram.duration==filtervalue).all()
    if filtertype=='type':
        courses = session.query(StudyProgram).filter(StudyProgram.type==filtervalue).all()
    if filtertype=='category':
        courses = session.query(StudyProgram).filter(StudyProgram.category==filtervalue).all()

    if len(courses) == 0:
        return "Sorry, I couldn't find any programs!"
        
    return f"I found the following results:\n" + \
    "\n".join([f"{i.entry_id} -> {i.coursecode}: {i.title}" for i in courses]) + \
    "\n\nPlease pick the numeric code to know more about the course"


def get_attribute_of_a_program(program: StudyProgram, attribute):
    if 'deadline' in attribute:
        return f"The deadline for {program.coursecode} are:\n {program.deadlines}"
    elif 'city' in attribute:
        return f"{program.coursecode} is taught in {program.city}"
    elif attribute in ['more info', 'more_info', 'more_information', 'more information']:
        return program.description
    elif 'course' in attribute:
        return f"These are the courses taught in {program.coursecode}: \n{program.courses}"
    elif 'link' in attribute:
        return f"These are the relevant links I found for {program.coursecode}: \n {program.link} \n{program.application_link}"
    elif 'application_link' in attribute:
        return f"Please check this link for the application: {program.application_link}"
    elif 'duration' in attribute:
        return f"{program.coursecode} runs for {program.duration}"
    elif 'language' in attribute:
        return f"{program.coursecode} is taught in {program.language_taught}"
    elif 'requirement' in attribute:
        return program.get_requirements()
    elif 'grade' in attribute:
        if program.grades_required:
            return f"You need to score {program.grades_required} to apply to {program.coursecode}"
        else:
            return "Couldn't find grades required for {program.coursecode}"

    else:
        return None


def convert_intent_json_to_response_string(intent_json):
    # program: all
    # program: all, category: cs
    # program: all, language: english
    
    # program -> ID, class: requirements
    # program -> ID, class: requirements, field: grade

    if intent_json['program'] == 'all':
        # means all or no filter for list of programs
        if 'category' in intent_json:
            # get program by category
            response_string = get_study_programs_by_query('category', intent_json['category'])
        elif 'language' in intent_json:
            # get program by language
            response_string = get_study_programs_by_query('language', intent_json['language'])
        else:
            # all programs
            response_string = get_all_courses()
    else:
        program = get_course_by_coursecode(intent_json['program'])
        if 'field' in intent_json:
            if intent_json['field'] == 'grade':
                # get grade of a program
                response_string = f"Required grades for {program.coursecode} is: {program.grades_required}"
            elif intent_json['field'] == 'language':
                # get grade of a program
                response_string = f"{program.coursecode} is taught in {program.languages_required}"
            elif intent_json['field'] == 'courses':
                # get courses of a program
                response_string = f"Courses taught in {program.coursecode} are: {program.courses}"
            elif intent_json['field'] == 'application_link':
                # get courses of a program
                response_string = f"Here is the application link for the program: {program.application_link}"
        else:
            # all requirements
            response_string = f"These are the general requirements for {program.coursecode}: {program.get_requirements()}"
    
    return response_string