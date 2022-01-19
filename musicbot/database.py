from typing import Optional, Any
import logging
from pathlib import Path
import attr
import psycopg2  # type: ignore
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)

DEFAULT_DB_ADMIN = 'postgres'
DEFAULT_DB_ADMIN_PASSWORD = 'postgres'

DEFAULT_DB_NAME = 'musicbot'
DEFAULT_DB_USER = 'musicbot'
DEFAULT_DB_PASSWORD = 'musicbot'
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_PORT = 5432
DEFAULT_DB_DSN = f'postgresql://{DEFAULT_DB_USER}:{DEFAULT_DB_PASSWORD}@{DEFAULT_DB_HOST}:{DEFAULT_DB_PORT}/{DEFAULT_DB_NAME}'


@attr.s(auto_attribs=True, frozen=True, repr=False)
class Database:
    dsn: str = DEFAULT_DB_DSN
    schemas = ['musicbot_public', 'musicbot_private']
    sql: Path = Path(__file__).resolve().parent / 'schema'

    @classmethod
    def from_params(cls, name: str, user: str, password: str, host: str, port: int) -> "Database":
        return Database(f'postgresql://{user}:{password}@{host}:{port}/{name}')

    def __repr__(self) -> str:
        representation = self.dsn
        if MusicbotObject.dry:
            representation += ' [DRY]'
        return representation

    def create_role_and_database(self, admin_password: Optional[str] = None, admin_user: Optional[str] = None) -> None:
        params = psycopg2.extensions.parse_dsn(self.dsn)
        host = params.pop('host')
        port = params.pop('port')
        name = params.pop('dbname')
        user = params.pop('user')
        password = params.pop('password')

        try:
            admin_connection = psycopg2.connect(user=user, password=password, host=host, port=port)
        except psycopg2.Error as e:
            logger.error(f"{e} : trying with admin credentials")
            admin_connection = psycopg2.connect(user=admin_user, password=admin_password, host=host, port=port)

        admin_connection.autocommit = True
        with admin_connection.cursor() as admin_cursor:
            admin_cursor.execute(f'''
do
$do$
begin
   if not exists (select from pg_catalog.pg_roles where rolname = '{user}') then
      create role {user} login password '{password}';
   end if;
end
$do$;
''')
            admin_cursor.execute(f"select count(*) = 1 from pg_catalog.pg_database where datname = '{name}'")
            result = admin_cursor.fetchone()
            if not result[0]:
                admin_cursor.execute(f'create database {name} with owner {user}')
            else:
                MusicbotObject.echo(f"{self} : already exists")

        admin_connection.close()

    def drop_database(self) -> None:
        params = psycopg2.extensions.parse_dsn(self.dsn)
        dbname = params.pop('dbname')
        host = params.pop('host')
        port = params.pop('port')
        user = params.pop('user')
        password = params.pop('password')
        admin_connection = psycopg2.connect(user=user, password=password, host=host, port=port)
        admin_connection.autocommit = True
        try:
            with admin_connection.cursor() as admin_cursor:
                self.kill_connections(admin_cursor, dbname)
                query = f'drop database if exists {dbname}'
                if not MusicbotObject.dry:
                    admin_cursor.execute(query)
                else:
                    MusicbotObject.tip(f'{self} : {query}')
        finally:
            admin_connection.close()

    def create_schemas(self) -> None:
        admin_connection = None
        try:
            admin_connection = psycopg2.connect(self.dsn)
            with admin_connection.cursor() as admin_cursor:
                try:
                    sql_files = [
                        sql_file
                        for sql_file in self.sql.iterdir()
                        if sql_file.is_file() and sql_file.suffix == '.sql'
                    ]
                    sql_files.sort()

                    for sql_file in sql_files:
                        MusicbotObject.echo(f'{self} : loading {sql_file}')
                        with open(sql_file, 'r', encoding="utf-8") as sql_file_handle:
                            admin_cursor.execute(sql_file_handle.read())
                except Exception as e:
                    MusicbotObject.err(f"{self} : {e}")
                    raise
            admin_connection.commit()
        except Exception as e:
            MusicbotObject.err(f"{self} : {e}")
            raise
        finally:
            if admin_connection:
                admin_connection.close()

    def kill_connections(self, cursor: Any, dbname: str) -> None:
        if not MusicbotObject.dry:
            cursor.execute(f'''
                select pg_terminate_backend(pg_stat_activity.pid)
                from pg_stat_activity
                where pg_stat_activity.datname = '{dbname}' and pid <> pg_backend_pid()''')
        else:
            MusicbotObject.tip(f"{self} : killing connections")

    def drop_functions(self, cursor: Any, schema: str) -> None:
        query = f'''
DO
$do$
DECLARE
   _sql text;
BEGIN
   SELECT INTO _sql
          string_agg(format('DROP %s %s;'
                          , CASE prokind
                              WHEN 'f' THEN 'FUNCTION'
                              WHEN 'a' THEN 'AGGREGATE'
                              WHEN 'p' THEN 'PROCEDURE'
                              WHEN 'w' THEN 'FUNCTION'  -- window function (rarely applicable)
                              -- ELSE NULL              -- not possible in pg 11
                            END
                          , oid::regprocedure)
                   , E'\n')
   FROM   pg_proc
   WHERE  pronamespace = '{schema}'::regnamespace  -- schema name here!
   -- AND    prokind = ANY ('{{f,a,p,w}}')         -- optionally filter kinds
   ;

   IF _sql IS NOT NULL THEN
      RAISE NOTICE '%', _sql;  -- debug / check first
      EXECUTE _sql;         -- uncomment payload once you are sure
   ELSE
      RAISE NOTICE 'No fuctions found in schema %', quote_ident(_schema);
   END IF;
END
$do$;'''
        try:
            cursor.execute(query)
        except psycopg2.Error:
            MusicbotObject.warn(f'{self} : {schema} does not exist')

    def drop_schemas(self) -> None:
        params = psycopg2.extensions.parse_dsn(self.dsn)
        dbname = params.pop('dbname')
        admin_connection = None
        try:
            try:
                admin_connection = psycopg2.connect(self.dsn)
            except psycopg2.OperationalError as e:
                MusicbotObject.warn(e)
                return
            admin_connection.autocommit = True

            with admin_connection.cursor() as admin_cursor:
                self.kill_connections(admin_cursor, dbname)
                for schema in self.schemas:
                    self.drop_functions(admin_cursor, schema)
                    query = f'drop schema if exists {schema} cascade'
                    MusicbotObject.echo(f"{self} : {query}")
                    if not MusicbotObject.dry:
                        admin_cursor.execute(query)

            admin_connection.commit()
        except Exception as e:
            MusicbotObject.err(f"{self} : {e}")
            raise
        finally:
            if admin_connection:
                admin_connection.close()

    def clear_schemas(self) -> None:
        self.drop_schemas()
        self.create_schemas()
