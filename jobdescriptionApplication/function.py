import openai
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def clean_paragraph(paragraph):
    if not isinstance(paragraph, str):
        return ""  # Return an empty string if the input is not a string

    patterns_to_remove = [
        r'Resource Innovations \(RI\)',
        r'a women-led',
        r'focused on impact',
        r'currently reside in the San Francisco CA Bay area',
        r'visa sponsorship or extensions',
        r'not offering',
        r'unfortunately',
        r'We require candidates to',
        r'With every step, we’re leading the charge to power change\.',
        r'Building on our expertise in',
        r'Description Ryanair Labs is the technology brand of Ryanair.',
        r'Labs is a state of-the-art digital & IT innovation',
        r'^\s*Description\s*',
        r'Methods is a.*?\.',
        r'About the role:',
        r'What Methods offer is to you:.*',
        r'Professional development.*',
        r'The benefits of our BA academy.*',
        r'\bTibra Capital\b',
        r'\bGoogle\b',
        r'\bMicrosoft\b',
        r'\bAmazon\b',
        r'\bFacebook\b',
        r'\bApple\b',
        r'\bTesla\b',
        r'\bRyanair\b',
        r'company\s\w+',  # Matches "company" followed by a word (e.g., "company Tibra")
        r'join\s\w+\s\w+',  # Matches "join Tibra Capital"
        r'\bat\s\w+',  # Matches "at Tibra"
        r'\bteam\s\w+',  # Matches "team Tibra"
        r'join our \w+',  # Matches "join our team"
        r'responsible for\b.*',
        r'Resource Innovations \(RI\)',
        r'a women-led',
        r'focused on impact',
        r'currently reside in the San Francisco CA Bay area',
        r'visa sponsorship or extensions',
        r'not offering',
        r'unfortunately',
        r'We require candidates to',
        r'With every step, we’re leading the charge to power change\.',
        r'Building on our expertise in',
        r'Description Ryanair Labs is the technology brand of Ryanair.',
        r'Labs is a state of-the-art digital & IT innovation',
        r'The Recruitment Process',
        r'Xplore has retained Bert Sadtler, President of Boxwood Strategies to manage all hiring',
        r'While this process is different, we feel that it genuinely offers both candidates and the best opportunity',
        r'Please click for a short video on the Boxwood Process',
        r'COMPENSATION.*?(?=\s[A-Z])',
        r'The Recruitment Process.*?(?=\s[A-Z])',
        r'While this process is different.*?(?=\s[A-Z])',
        r'Boxwood Process.*?(?=\s[A-Z])'
        r'SmartLogic '

    ]

    cleaned_text = paragraph
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, '', cleaned_text)

    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text

def combine_requirements(df):
    # Combine 'Requirement' and 'Requirements' columns into 'Combined_Requirements'
    df['Combined_Requirements'] = (df['Requirement'].fillna('') + ' ' + df['Requirements'].fillna('')).str.strip()

    # Drop the original columns
    df.drop(columns=['Requirement', 'Requirements'], inplace=True)

    return df

def find_most_similar_job_details(df, new_job_titles):
    job_titles = df['Category'].tolist()
    descriptions = df['Description'].tolist()
    requirements = df['Combined_Requirements'].tolist()
    similar_details = {}

    for new_job_title in new_job_titles:
        embeddings = [get_embedding(title) for title in job_titles]
        embeddings.append(get_embedding(new_job_title))

        # Calculate cosine similarity
        numpy_array = np.array(embeddings)
        new_job_title_embedding = numpy_array[-1].reshape(1, -1)
        job_title_embeddings = numpy_array[:-1]

        similarities = cosine_similarity(new_job_title_embedding, job_title_embeddings)[0]
        most_similar_index = np.argmax(similarities)

        # Clean up the description and requirements
        cleaned_description = clean_paragraph(descriptions[most_similar_index])
        cleaned_requirements = clean_paragraph(requirements[most_similar_index])

        # Shorten the description if necessary (e.g., only the first 2 sentences)
        cleaned_description = '. '.join(cleaned_description.split('. ')[:2])

        similar_details[new_job_title] = {
            'description': cleaned_description,
            'requirements': cleaned_requirements
        }

    return similar_details

