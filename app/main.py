from fastapi import FastAPI, Response, status, HTTPException

from pydantic import BaseModel
from typing import Optional
import time

import psycopg2
from psycopg2.extras import RealDictCursor


class Post(BaseModel):
    title: str 
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="MySocialApp",
                                user="postgres", password="admin123", 
                                cursor_factory=RealDictCursor) # for column names
        cursor = conn.cursor()
        print("Database connected successfully...")
        break
    except Exception as err:
        print("Database connection failed...")
        print(f"Error: {str(err)}")
        time.sleep(2)




app = FastAPI()


my_posts = [{"id": 1, "title": "First Post", "content": "Content of the first post"}]


@app.get("/")
def home_page():
    return {"message": "Hello, World!"}


@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM POSTS """)
    posts = cursor.fetchall()
    return {"data": posts}

# from fastapi.params import Body
# @app.post("/posts/create")
# def create_post(payload: dict = Body(...)):
#     return {"message": 
#             f"Post with title: {payload['title']} and "
#             f"content:{payload['content']} created successfully"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, response: Response):
    cursor.execute("""INSERT INTO POSTS (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM POSTS WHERE ID=%s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} is not found.")
    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    for idx, post in enumerate(my_posts):
        if post["id"] == id:
            my_posts.pop(idx)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post with id {id} is not found.")


@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, updated_post: Post):
    for idx, post in enumerate(my_posts):
        if post["id"] == id:
            updated_post_dict = updated_post.model_dump()
            updated_post_dict['id'] = id
            my_posts[idx] = updated_post_dict
            return {"data": updated_post_dict}
    if updated_post_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} is not found.")
