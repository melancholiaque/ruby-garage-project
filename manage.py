import click


@click.group()
def CLI():
    """
    CLI utilities collection for various tasks associated with project
    """
    pass


@CLI.command()
@click.option('--no-debug', is_flag=True,
              help='disables debug error messaging and on-fly server reboots')
def run(no_debug):
    """
    start server
    """
    from todoapp import app
    app.run(debug=(not no_debug))


@CLI.command('tables-init')
def tables_init():
    """
    database table initialization
    """
    from todoapp.data import Project, Task, User

    for table, table_name in [(User, 'user'),
                              (Project, 'project'),
                              (Task, 'task')]:
        try:
            table.create_table()
        except Exception as e:
            print(f'{table_name} table error {type(e)}:{e}\
            check your postgre server and premissions')
        else:
            print(f'{table_name} table initializaed successfully')


@CLI.command('tables-drop')
@click.option('--yes', is_flag=True,
              callback=lambda ctx, _, val: not val and ctx.abort(),
              expose_value=False,
              prompt='Drop database? (all data will be lost)')
def tables_drop():
    """
    database table deletion
    """
    from todoapp.data import db, Project, Task, User
    db.drop_tables((Task,Project,User))
    print('data tables dropped successfully')


if __name__ == '__main__':
    CLI()
