import logging
import subprocess
import signal
import os
import click
from musicbot import lib
from musicbot.config import config
from musicbot.backend.database import MB_DB, DEFAULT_DB

logger = logging.getLogger(__name__)

MB_BACKGROUND = 'MB_BACKGROUND'
DEFAULT_BACKGROUND = False
background_option = [click.option('--background', envvar=MB_BACKGROUND, help='Run in background', is_flag=True, show_default=True)]

MB_JWT_SECRET = 'MB_JWT_SECRET'
DEFAULT_JWT_SECRET = 'my_little_secret'
jwt_secret_argument = [click.argument('jwt_secret')]
jwt_secret_option = [click.option('--jwt-secret', envvar=MB_JWT_SECRET, help='Secret to sign tokens', default=DEFAULT_JWT_SECRET, show_default=False)]

MB_GRAPHQL_PUBLIC_PORT = 'MB_GRAPHQL_PUBLIC_PORT'
DEFAULT_GRAPHQL_PUBLIC_PORT = 5000
graphql_public_port_option = [click.option('--graphql-public-port', envvar=MB_GRAPHQL_PUBLIC_PORT, help='Postgraphile public API port', default=DEFAULT_GRAPHQL_PUBLIC_PORT, show_default=True)]

MB_GRAPHQL_PUBLIC_INTERFACE = 'MB_GRAPHQL_PUBLIC_INTERFACE'
DEFAULT_GRAPHQL_PUBLIC_INTERFACE = 'localhost'
graphql_public_interface_option = [click.option('--graphql-public-interface', envvar=MB_GRAPHQL_PUBLIC_INTERFACE, help='Postgraphile public API interface', default=DEFAULT_GRAPHQL_PUBLIC_INTERFACE, show_default=True)]

public_options = jwt_secret_argument + graphql_public_port_option + graphql_public_interface_option + background_option

MB_GRAPHQL_PRIVATE_PORT = 'MB_GRAPHQL_PRIVATE__PORT'
DEFAULT_GRAPHQL_PRIVATE_PORT = 5001
graphql_private_port_option = [click.option('--graphql-private-port', envvar=MB_GRAPHQL_PRIVATE_PORT, help='Postgraphile private API port', default=DEFAULT_GRAPHQL_PRIVATE_PORT, show_default=True)]

MB_GRAPHQL_PRIVATE_INTERFACE = 'MB_GRAPHQL_PRIVATE_INTERFACE'
DEFAULT_GRAPHQL_PRIVATE_INTERFACE = 'localhost'
graphql_private_interface_option = [click.option('--graphql-private-interface', envvar=MB_GRAPHQL_PRIVATE_INTERFACE, help='Postgraphile private API interface', default=DEFAULT_GRAPHQL_PRIVATE_INTERFACE, show_default=True)]

private_options = graphql_private_port_option + graphql_private_interface_option + background_option


class Postgraphile:
    def __init__(self, cmd, db, interface, port, dsn=None, jwt_secret=None):
        self.cmd = cmd
        self.db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
        self.jwt_secret = jwt_secret if jwt_secret is not None else os.getenv(MB_JWT_SECRET, DEFAULT_JWT_SECRET)
        self.interface = interface if interface is not None else os.getenv(MB_GRAPHQL_PUBLIC_INTERFACE, DEFAULT_GRAPHQL_PUBLIC_INTERFACE)
        self.port = port if port is not None else int(os.getenv(MB_GRAPHQL_PUBLIC_PORT, str(DEFAULT_GRAPHQL_PUBLIC_PORT)))
        self.process = None
        self.dsn = dsn if dsn is not None else "http://{}:{}/graphql".format(self.interface, self.port)

    def run(self, background=None):
        background = background if background is not None else lib.str2bool(os.getenv(MB_BACKGROUND, str(DEFAULT_BACKGROUND)))
        if not self.process:
            if background:
                # self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True, start_new_session=True)
                print(os.getpgid(self.process.pid))
            else:
                os.system(self.cmd)
                self.process = True
        else:
            logger.warning('Postgraphile running, in background? : %s', background)

    def kill(self):
        if self.process not in [None, True, False]:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

    @classmethod
    def public(cls, db=None, jwt_secret=None, interface=None, port=None):
        db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
        interface = interface if interface is not None else os.getenv(MB_GRAPHQL_PUBLIC_INTERFACE, DEFAULT_GRAPHQL_PUBLIC_INTERFACE)
        port = port if port is not None else int(os.getenv(MB_GRAPHQL_PUBLIC_PORT, str(DEFAULT_GRAPHQL_PUBLIC_PORT)))

        base_cmd_fmt = """npx postgraphile --cors --no-setof-functions-contain-nulls --no-ignore-rbac --no-ignore-indexes --dynamic-json -c {} -n {} -p {} --schema musicbot_public --default-role musicbot_anonymous --jwt-token-identifier musicbot_public.jwt_token --jwt-secret {} -l 10MB --append-plugins `pwd`/vue-musicbot/node_modules/postgraphile-plugin-connection-filter --simple-collections both"""
        base_cmd = base_cmd_fmt.format(db, interface, port, jwt_secret)

        if config.debug:
            cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --enhance-graphiql --show-error-stack --watch""".format(base_cmd)
        else:
            cmd = """{} --disable-graphiql --disable-query-log""".format(base_cmd)
        logger.info(cmd)
        self = Postgraphile(cmd, db, jwt_secret=jwt_secret, interface=interface, port=port)
        return self

    @classmethod
    def private(cls, db=None, interface=None, port=None):
        db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
        interface = interface if interface is not None else os.getenv(MB_GRAPHQL_PRIVATE_INTERFACE, DEFAULT_GRAPHQL_PRIVATE_INTERFACE)
        port = port if port is not None else int(os.getenv(MB_GRAPHQL_PRIVATE_PORT, str(DEFAULT_GRAPHQL_PRIVATE_PORT)))

        base_cmd = """npx postgraphile --cors --include-extension-resources --no-setof-functions-contain-nulls --no-ignore-indexes --dynamic-json -c {} -n {} -p {} --schema musicbot_public,musicbot_private --default-role postgres --append-plugins `pwd`/vue-musicbot/node_modules/postgraphile-plugin-connection-filter --enhance-graphiql --simple-collections both""".format(db, interface, port)

        cmd = """{} --disable-graphiql --disable-query-log""".format(base_cmd)
        if config.debug:
            cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --show-error-stack --watch""".format(base_cmd)
        logger.info(cmd)
        self = Postgraphile(cmd, db, interface=interface, port=port)
        return self
