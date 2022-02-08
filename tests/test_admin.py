# type: ignore
import logging
import json
import pytest
from click_skeleton.testing import run_cli
from musicbot.main import cli
from . import fixtures

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
def test_admin(cli_runner, user_token, postgraphile_private):  # pylint: disable=unused-argument
    users_json = run_cli(cli_runner, cli, [
        '--quiet',
        'user', 'list',
        '--output', 'json',
        '--graphql-admin', postgraphile_private,
    ])
    users = json.loads(users_json)
    for user in users:
        if user['email'] == fixtures.email and user['firstName'] == fixtures.first_name and user['lastName'] == fixtures.last_name:
            break
    else:
        pytest.fail("test user not detected")
