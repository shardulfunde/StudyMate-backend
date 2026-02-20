from celery import Celery

celery = Celery(
    "studymate",
    broker="redis://localhost:6379/0",
)


celery.conf.update(
    include=["app.tasks.embedding"]
)
