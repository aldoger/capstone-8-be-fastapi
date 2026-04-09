from invoke import task

@task
def server(c):
    c.run("uvicorn app.main:app --reload")