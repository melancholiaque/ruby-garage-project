import peewee

database = peewee.PostgresqlDatabase("todo-app-database")

class Project(peewee.Model):
    """
    ORM for projects
    """
    #id created internally
    name = peewee.CharField()

    class Meta:
        database = database
                        

class Task(peewee.Model):
    """
    ORM for tasks
    """
    #id created internally
    name = peewee.CharField()
    status = peewee.CharField()
    project_id = peewee.ForeignKeyField(Project)

    class Meta:
        database = database
