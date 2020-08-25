import json
import pytest
from musicbot.cli import cli
from musicbot.click_helpers import run_cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_admin(cli_runner, user_token, postgraphile_private):  # pylint: disable=unused-argument
    users_json = run_cli(cli_runner, cli, ['user', 'list', '--output', 'json', '--graphql-admin', postgraphile_private])
    users = json.loads(users_json)
    for user in users:
        if user['email'] == fixtures.email and user["user"]['firstName'] == fixtures.first_name and user["user"]['lastName'] == fixtures.last_name:
            break
    else:
        pytest.fail("test user not detected")
