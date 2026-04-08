from invoke import task

@task
def run(c):
    c.run("python main.py yolo")

@task
def server(c):
    c.run("uvicorn app.main:app --reload")

@task
def all(c):
    c.run("uvicorn app.main:app --reload & python main.py yolo")