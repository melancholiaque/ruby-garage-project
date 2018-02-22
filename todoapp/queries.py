import psycopg2

class DbBinding():

    def __init__(self,*args,**kwargs):
        self.conn = psycopg2.connect(*args,,**kwargs)

    def get_statuses(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT DISTINCT name,status FROM task ORDER BY name;'
                )
                cur.execute(SQL)
                return cur.fetchall()

    def list_by_task_count(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT project.name,COUNT(task) '
                    'FROM project '
                    'INNER JOIN task ON task.project_id=project.id '
                    'GROUP BY project.name '
                    'ORDER BY COUNT(task) DESC; '
                )
                cur.execute(SQL)
                return cur.fetchall()

    def list_by_proj_name(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT project.name,COUNT(task) '
                    'FROM project '
                    'INNER JOIN task '
                    'ON task.project_id=project.id GROUP BY project.name '
                    'ORDER BY project.name ASC; '
                )
                cur.execute(SQL)
                return cur.fetchall()

    def startswith_N(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT task.name,project.name FROM task '
                    'INNER JOIN project '
                    'ON project.id = task.project_id '
                    "WHERE project.name LIKE 'N%';"
                )
                cur.execute(SQL)
                return cur.fetchall()

    def with_a(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT project.name,COUNT(task) '
                    'FROM project '
                    'LEFT JOIN task ON task.project_id=project.id '
                    "WHERE project.name LIKE '%a%' "
                    'GROUP BY project.name '
                    'ORDER BY COUNT(task) DESC;'
                )
                cur.execute(SQL)
                return cur.fetchall()

    def duplicates(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT name, COUNT(*) '
                    'FROM task '
                    'GROUP BY name '
                    'HAVING COUNT(*)>1;'
                )
                cur.execute(SQL)
                return cur.fetchall()

    def Garage(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT task.name,status,COUNT(*) '
                    'FROM task '
                    "INNER JOIN project ON project.name='Garage'\
                                        AND task.project_id=project.id "
                    'GROUP BY task.name, status '
                    'HAVING COUNT(*)>1;'
                )
                cur.execute(SQL)
                return cur.fetchall()

    def ten_plus(self):
        with self.conn:
            with self.conn.cursor() as cur:
                SQL = (
                    'SELECT project.name,COUNT(task) '
                    'FROM project '
                    'LEFT JOIN task ON task.project_id=project.id\
                                    AND task.status=True '
                    'GROUP BY project.name '
                    'HAVING COUNT(task) > 10 '
                    'ORDER BY COUNT(task) DESC;'
                )
                cur.execute(SQL)
                return cur.fetchall()

    def test(self):
        queries = ('get_statuses',
                   'list_by_task_count',
                   'list_by_proj_name',
                   'startswith_N',
                   'with_a',
                   'duplicates',
                   'Garage',
                   'ten_plus',
        )

        methods = ((q,getattr(self,q)) for q in queries)

        for name,meth in methods:
            print(name)
            for i in meth():
                print(i)
            print()

if __name__=='__main__':
    import psycopg2
    import urllib.parse as urlparse
    import os

    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    d = DbBinding(dbname=dbname,
                  user=user,
                  password=password,
                  host=host,
                  port=port)
    d.test()
