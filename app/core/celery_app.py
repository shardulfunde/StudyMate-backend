from celery import Celery

celery = Celery(
    "studymate",
    broker="redis://localhost:6379/0",
)

celery.conf.task_routes = {
    "app.tasks.embedding.generate_embeddings": {"queue": "embeddings"}
}


celery.conf.update(
    include=["app.tasks.embedding"]
)
