"""
Database module is responsible for:
providing Task model,
providing simple orm functions
for retrieving, creating and updating tasks
"""


from project.app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(15), nullable=False, index=True)
    status = db.Column(db.String(15), default='processing')
    location = db.Column(db.String(255), nullable=True)


def get_task(url, data_type):
    return db.session.query(Task).filter_by(url=url, type=data_type).first()


def create_task(url, data_type):
    task = db.session.query(Task).filter_by(url=url, type=data_type).first()
    if task:
        task.status = 'processing'
    else:
        task = Task(url=url, type=data_type)
    db.session.add(task)
    db.session.commit()
    return task.id


def update_task_ready(task_id, location):
    task = db.session.query(Task).filter_by(id=task_id).first()
    task.status = 'ready'
    task.location = location
    db.session.add(task)
    db.session.commit()
