import random
import sqlite3 as sldb
from typing import Any

class DatabaseClient:
    
    def __init__(self) -> None:
        self.con = sldb.connect('questions.sqlite3')
        self.cur = self.con.cursor()
        self.get_no_of_questions()

    def get_no_of_questions(self) -> int:
        query = 'SELECT COUNT(*) from questions'
        self.cur.execute(query)
        response = self.cur.fetchone()
        self.questions_count =  response[0]
    
    def format_question(self, question) -> dict:
        return {
            'id': int(question[0]),
            'title': question[1],
            'slug': question[2],
            'difficulty': question[3],
            'has_solution': bool(question[4])
        }
    
    def get_question_with_id(self, id) -> Any:
        query = f'SELECT * from questions where id="{id}"'
        self.cur.execute(query)
        question = self.cur.fetchone()
        return self.format_question(question)
    
    def get_random_question(self) -> Any:
        random_index = random.choice(range(1, self.questions_count + 1))
        random_question = self.get_question_with_id(random_index)
        return random_question
    
    def get_questions_with_difficulty(self, dif) -> list:
        query = f'SELECT * from questions where difficulty={dif}'
        self.cur.execute(query)
        questions = self.cur.fetchall()
        return questions
    
    def get_random_question_with_difficulty(self, dif) -> Any:
        questions = self.get_questions_with_difficulty(dif)
        question = random.choice(questions)
        return self.format_question(question)

if __name__ == "__main__":
    client = DatabaseClient()
    print(client.get_random_question())