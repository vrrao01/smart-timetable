from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gunicorn
from pydantic import BaseModel
import numpy as np
import pandas as pd
import re
import string

# created Python modules
import ocr
import courses

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# pydantic models


class request_generate(BaseModel):
    url: str


class request_my_courses(BaseModel):
    roll_number: str


@app.get('/')
def welcome():
    return {'ping': 'Hello there! Go to /docs to see the Swagger documentation'}


@app.post('/generate-all-courses')
def generate_all_courses(data: request_generate):
    url = data.url
    message = ocr.generate_all_courses_CSV(url)
    if message == None:
        return HTTPException(status_code=400, detail='Invalid PDF or URL')
    else:
        return message


def return_empty_string(value):
    return '' if pd.isnull(value) else value


@app.post('/get-my-courses')
def get_my_courses(data: request_my_courses):
    roll_number = data.roll_number
    courses_parsed = courses.get_courses_parsed(roll_number)

    # Store all courses in a DF
    all_courses_df = ocr.fetch_all_courses_DF()
    if (all_courses_df.empty):
        return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')

    # Find all course details given the course code list
    my_courses_df = all_courses_df.loc[all_courses_df['1'].isin(
        courses_parsed)]

    data = {'roll_number': roll_number}
    my_courses_list = []

    for i in range(0, len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]
        my_courses = {
            'code': return_empty_string(df_entry[1]),
            'course': return_empty_string(df_entry[2]),
            'ltpc': return_empty_string(df_entry[3]),
            'slot': return_empty_string(df_entry[8]),
            'instructor': return_empty_string(df_entry[11]),
            'midsem': return_empty_string(df_entry[9]),
            'endsem': return_empty_string(df_entry[10])
        }
        my_courses_list.append(my_courses)

    data['courses'] = my_courses_list

    if (len(my_courses_list) == 0):
        return HTTPException(status_code=400, detail='Invalid roll number')

    return data


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
