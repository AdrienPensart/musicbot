import click
import logging
import os
from musicbot.config import config
from musicbot.backend.database import MB_DB, DEFAULT_DB

logger = logging.getLogger(__name__)


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

public_options = jwt_secret_argument + graphql_public_port_option + graphql_public_interface_option

MB_GRAPHQL_PRIVATE_PORT = 'MB_GRAPHQL_PRIVATE__PORT'
DEFAULT_GRAPHQL_PRIVATE_PORT = 5001
graphql_private_port_option = [click.option('--graphql-private-port', envvar=MB_GRAPHQL_PRIVATE_PORT, help='Postgraphile private API port', default=DEFAULT_GRAPHQL_PRIVATE_PORT, show_default=True)]

MB_GRAPHQL_PRIVATE_INTERFACE = 'MB_GRAPHQL_PRIVATE_INTERFACE'
DEFAULT_GRAPHQL_PRIVATE_INTERFACE = 'localhost'
graphql_private_interface_option = [click.option('--graphql-private-interface', envvar=MB_GRAPHQL_PRIVATE_INTERFACE, help='Postgraphile private API interface', default=DEFAULT_GRAPHQL_PRIVATE_INTERFACE, show_default=True)]

private_options = graphql_private_port_option + graphql_private_interface_option


def public(db=None, jwt_secret=None, graphql_public_interface=None, graphql_public_port=None):
    db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
    jwt_secret = jwt_secret if jwt_secret is not None else os.getenv(MB_JWT_SECRET, DEFAULT_JWT_SECRET)
    graphql_public_interface = graphql_public_interface if graphql_public_interface is not None else os.getenv(MB_GRAPHQL_PUBLIC_INTERFACE, DEFAULT_GRAPHQL_PUBLIC_INTERFACE)
    graphql_public_port = graphql_public_port if graphql_public_port is not None else os.getenv(MB_GRAPHQL_PUBLIC_PORT, DEFAULT_GRAPHQL_PUBLIC_PORT)

    base_cmd_fmt = """npx postgraphile --no-setof-functions-contain-nulls --no-ignore-rbac --no-ignore-indexes --dynamic-json -c {} -n {} -p {} --schema musicbot_public --default-role musicbot_anonymous --jwt-token-identifier musicbot_public.jwt_token --jwt-secret {} -l 10MB --append-plugins postgraphile-plugin-connection-filter --simple-collections both"""
    base_cmd = base_cmd_fmt.format(db, graphql_public_interface, graphql_public_port, jwt_secret)

    if config.debug:
        cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --enhance-graphiql --show-error-stack --watch""".format(base_cmd)
    else:
        cmd = """{} --disable-graphiql --disable-query-log""".format(base_cmd)
    logger.info(cmd)
    return cmd


def private(db=None, graphql_private_interface=None, graphql_private_port=None):
    db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
    graphql_private_interface = graphql_private_interface if graphql_private_interface is not None else os.getenv(MB_GRAPHQL_PRIVATE_INTERFACE, DEFAULT_GRAPHQL_PRIVATE_INTERFACE)
    graphql_private_port = graphql_private_port if graphql_private_port is not None else os.getenv(MB_GRAPHQL_PRIVATE_PORT, DEFAULT_GRAPHQL_PRIVATE_PORT)

    base_cmd = """npx postgraphile --include-extension-resources --no-setof-functions-contain-nulls --no-ignore-indexes --dynamic-json -c {} -n {} -p {} --schema musicbot_public,musicbot_private --default-role postgres --append-plugins postgraphile-plugin-connection-filter --enhance-graphiql --simple-collections both""".format(db, graphql_private_interface, graphql_private_port)

    if config.debug:
        cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --show-error-stack --watch""".format(base_cmd)
    else:
        cmd = """{} --disable-graphiql --disable-query-log""".format(base_cmd)
    logger.info(cmd)
    return cmd
