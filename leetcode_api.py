import requests
import json

import sqlite3 as sldb

url = "https://leetcode.com/graphql/"

def get_leetcode_questions():
    questions = []
    current_index = 0
    LIMIT = 50
    query = """query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
            acRate
            difficulty
            questionId
            paidOnly: isPaidOnly
            title
            titleSlug
            topicTags {
                name
                id
                slug
            }
            hasSolution
            }
        }
    }"""
    headers = {
        'Content-Type': 'application/json'
    }
    while True:
        variables = {
        "categorySlug": "",
        "skip": current_index,
        "limit": LIMIT,
        "filters": {}
        }

        payload = json.dumps(
            {
                'query': query,
                'variables': variables
            }
        )

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        total = data['data']['problemsetQuestionList']['total']
        questions_data = data['data']['problemsetQuestionList']['questions']
        questions += questions_data
        print(f"Acquired {len(questions)}/{total} questions", end="\r")
        if len(questions_data) < LIMIT:
            break
        else:
            current_index += LIMIT
    return questions

def create_mm_questions_topics_table(cur):
    query = """CREATE TABLE IF NOT EXISTS questions_topics_mm (
        question_id,
        topic_id,
        FOREIGN KEY(question_id) REFERENCES questions(id),
        FOREIGN KEY(topic_id) REFERENCES topics(id),
        UNIQUE(question_id, topic_id)
    )"""
    cur.execute(query)

def create_topics_table(cur):
    query = """CREATE TABLE IF NOT EXISTS topics(
        id TEXT NOT NULL PRIMARY KEY,
        name TEXT,
        slug TEXT,
        UNIQUE(slug)
    )"""
    cur.execute(query)

def create_questions_table(cur):
    query = """CREATE TABLE IF NOT EXISTS questions(
        id NOT NULL PRIMARY KEY,
        title TEXT,
        title_slug TEXT,
        difficulty TEXT,
        has_solution BOOLEAN,
        UNIQUE(title_slug)
    )"""
    cur.execute(query)

def init_questions_database():
    con = sldb.connect('questions.sqlite3')
    cur = con.cursor()
    create_questions_table(cur)
    create_topics_table(cur)
    create_mm_questions_topics_table(cur)
    return con, cur

def add_question(cur, id, title, title_slug, difficulty, has_solution):
    query = "INSERT OR REPLACE into questions (id, title, title_slug, difficulty, has_solution) VALUES (?, ?, ?, ?, ?)"
    cur.execute(query, (id, title, title_slug, difficulty, has_solution))

def add_topic(cur, id, name, slug):
    query = "INSERT OR REPLACE INTO topics (id, name, slug) VALUES (?, ? ,?)"
    cur.execute(query, (id, name, slug))

def add_question_topic_relation(cur, question_id, topic_id):
    query = "INSERT OR IGNORE INTO questions_topics_mm (question_id, topic_id) VALUES (?, ?)"
    cur.execute(query, (question_id, topic_id))

def add_questions(cur, questions):
    for question in questions:
        add_question(cur, question.get("questionId", "0"), question.get("title", ""), question.get("titleSlug", ""), question.get("difficulty", ""), question.get("hasSolution", False))
        topics = question.get("topicTags", [])
        for topic in topics:
            add_topic(cur, topic.get("id", 0), topic.get("name", ""), topic.get("slug"))
            add_question_topic_relation(cur, question.get("questionId", "0"), topic.get("id", 0))

def fetch_questions():
    print("Retrieving questions from leetcode")
    questions = get_leetcode_questions()
    print("\nInitializing Database...")
    con, cur = init_questions_database()
    print("Updating Database..")
    add_questions(con, questions)
    con.commit()
    print("Fetch Successful")
    con.close()

if __name__ == "__main__":
    fetch_questions()