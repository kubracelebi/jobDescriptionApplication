from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from function import find_most_similar_job_details, combine_requirements
from Database import create_db_and_tables, get_session, insert_job_details
from sqlmodel import Session

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    df = pd.read_csv("job_description.csv", index_col=0)
    categories = df['Category'].unique().tolist()
    return templates.TemplateResponse("index.html", {"request": request, "categories": categories})

@app.post("/process-csv/", response_class=HTMLResponse)
async def process_csv(request: Request, category: str = Form(...), session: Session = Depends(get_session)):
    df = pd.read_csv("job_description.csv", index_col=0)
    df = combine_requirements(df)  # Combine 'Requirement' and 'Requirements'

    similar_details = find_most_similar_job_details(df, [category])

    for details in similar_details.values():
        insert_job_details(session, category, details['description'], details['requirements'])

    # Pass the zip function to the template context
    return templates.TemplateResponse("result.html", {
        "request": request,
        "descriptions": [details['description'] for details in similar_details.values()],
        "requirements": [details['requirements'] for details in similar_details.values()],
        "zip": zip
    })