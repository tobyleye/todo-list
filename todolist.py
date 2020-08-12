from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, nullable=False)
    deadline = Column(Date, default=datetime.today())

    def __str__(self):
        return f'{self.task}'


# create table in db
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def prompt_user():
    return input('>')


def print_tasks_or_nothing(tasks, formatter=lambda task: f'{task}', fallback='Nothing to do', **kwargs):
    if tasks:
        for n, task in enumerate(tasks, 1):
            print(f'{n}. {formatter(task)}', **kwargs)
    else:
        print(fallback, **kwargs)


def today_task():
    today = datetime.today()
    tasks = session.query(Task).filter(Task.deadline == today.date()).all()
    print('\nToday {}:'.format(today.strftime('%d %b')))
    print_tasks_or_nothing(tasks)


def week_task():
    today = datetime.today()
    for i in range(0, 7):
        when = today + timedelta(days=i)
        tasks = session.query(Task).filter(Task.deadline == when.date()).all()
        print('\n{}:'.format(when.strftime('%A %d %b')))
        print_tasks_or_nothing(tasks, end='\n')


def all_task():
    tasks = session.query(Task).order_by(Task.deadline).all()
    print('\nAll tasks:')
    print_tasks_or_nothing(tasks, formatter=lambda task: f"{task.task}. {task.deadline.strftime('%d %b')}")


def add_task():
    print('\nEnter task')
    task = prompt_user()
    print('Enter deadline')
    deadline = prompt_user()
    new_task = Task(task=task, deadline=datetime.strptime(deadline, '%Y-%m-%d'))
    session.add(new_task)
    session.commit()
    print('The task has been added!')


def delete_task():
    print('\nChoose the number of the task you want to delete:')
    tasks = session.query(Task).all()
    print_tasks_or_nothing(tasks, formatter=lambda task: f"{task} {task.deadline.strftime('%d %b')}")
    task_to_delete = tasks[int(prompt_user()) - 1]
    session.delete(task_to_delete)
    session.commit()
    print('The task has been deleted')


def missed_task():
    tasks = session.query(Task).filter(Task.deadline < datetime.today().date()).all()
    print('\nMissed tasks:')
    print_tasks_or_nothing(tasks, fallback='Nothing is missed!')


def exit():
    global is_running
    print('\nBye!')
    is_running = False


# menu arranged in order of presentation
menu = {
    1: ("Today's tasks", today_task),
    2: ("Week's tasks", week_task),
    3: ("All tasks", all_task),
    4: ('Missed tasks', missed_task),
    5: ('Add task', add_task),
    6: ('Delete task', delete_task),
    0: ('Exit', exit)
}
formatted_menu = [f'{i}) {menu[i][0]}' for i in menu]
is_running = True

while is_running:
    print(*formatted_menu, sep='\n')
    user_choice = int(prompt_user())
    if user_choice in menu:
        # run callback
        menu[user_choice][1]()
    else:
        print('Invalid choice')
    print()
