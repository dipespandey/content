import requests
from bs4 import BeautifulSoup
from typing import List
from dataclasses import field
from dataclasses import dataclass


@dataclass
class Requirement:
    deadlines: str
    languages: str
    credits: str
    other: str
    grade: str


@dataclass
class StudyProgram:
    id: str
    title: str
    link: str
    category: str
    duration: str
    credits: str
    city: str
    type: str
    description: str
    language_taught: str
    courses: str
    level: str
    requirements: Requirement = field(default_factory=Requirement)


def get_all_courses(path):
    with open(path) as content:
        soup = BeautifulSoup(content, 'html.parser')
    programs: List[StudyProgram] = []
    courses = soup.find_all('li', attrs={'class': 'Item'})
    for i in courses:
        program = convert_li_to_program(i)
        programs.append(program)
    return programs


def get_individual_course(url):
    content = requests.get('https://www.ntnu.edu/studies/macs').text
    soup = BeautifulSoup(content, 'html.parser')
        



def convert_li_to_program(item):
    link = item.find('a', href=True)['href']
    title, level = item.find('span').text.split(' - ')
    attrs = item.find('p').text.split(' | ')
    print(attrs)
    if len(attrs) == 4:
        level_years, city, degree_type, language = attrs
    else:
        language = 'Norsk'
        level_years, city, degree_type = attrs
    if 'years' in level_years:
        _, years = level_years.split(' - ')
    else:
        years = None
    
    return StudyProgram(title, link, years, city, degree_type, '', language, level)

