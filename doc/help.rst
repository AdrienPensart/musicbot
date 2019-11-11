========
MusicBot
========
+---------------+-----------------+
|     Tools     |      Result     |
+===============+=================+
|     Codacy    |    |codacy|     |
+---------------+-----------------+
|     Coverage  |   |coverage|    |
+---------------+-----------------+

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/621acf3309b24c538c40824f9af467de
   :target: https://www.codacy.com/app/AdrienPensart/musicbot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=AdrienPensart/musicbot&amp;utm_campaign=Badge_Grade
   :alt: Codacy badge
.. |coverage| image:: https://github.com/AdrienPensart/musicbot/blob/master/doc/coverage.svg
   :alt: Coverage badge

Description
-----------
CLI / API / Website to manipulate music and create smart playlists, and play it !

It uses poetry tool to manage project life.

Installation
------------

.. code-block:: bash

  sudo apt install -y build-essential libtag1-dev ffmpeg postgresql-12 libpcre3-dev postgresql-server-dev-all docker.io libchromaprint-tools libbz2-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev tk-dev liblzma-dev libssl-dev libreadline-dev
  sudo usermod -aG docker $USER

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  https://pyenv.run | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  python <(curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py) --preview
  poetry install

  echo "shared_preload_libraries = 'pg_stat_statements'" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
  echo "pg_stat_statements.track = all" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
  sudo systemctl restart postgresql
  sudo -u postgres psql -d postgres -c "create user postgres with password 'musicbot' superuser;" && history -c
  sudo -u postgres psql -d postgres -c "alter user postgres password 'musicbot';" && history -c
  poetry run pgcli postgresql://postgres:musicbot@localhost:5432

  git clone https://github.com/nginx/nginx.git
  git clone https://github.com/evanmiller/mod_zip.git
  cd nginx
  auto/configure --prefix=/opt/nginx --add-module="$HOME/mod_zip" --with-http_auth_request_module
  sudo make install
  sudo ln -s $HOME/musicbot/scripts/musicbot.service /etc/systemd/system/musicbot.service
  sudo ln -s $HOME/musicbot/scripts/nginx.service /etc/systemd/system/nginx.service
  sudo rm /opt/nginx/conf/nginx.conf
  sudo ln -s $HOME/musicbot/scripts/nginx.conf /opt/nginx/conf/nginx.conf
  sudo ln -s /opt/nginx/sbin/nginx /usr/sbin/nginx

  git clone https://github.com/michelp/pgjwt.git
  cd pgjwt
  sudo make install

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload

  # in your user folder
  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
  nvm install node
  npm install yarn -g
  cd $HOME/musicbot/vue-musicbot
  yarn install

Testing
------------

.. code-block:: bash

poetry run pytest --disable-warnings --cov-report term-missing --cov musicbot -x -n auto tests

Linting
------------

.. code-block:: bash

poetry run pylint -d line-too-long,too-many-arguments,protected-access,missing-docstring,invalid-name,too-many-public-methods,too-many-instance-attributes,duplicate-code,too-many-nested-blocks,too-many-branches,too-many-return-statements,too-many-statements,too-many-locals,too-few-public-methods,too-many-ancestors,abstract-method,anomalous-backslash-in-string musicbot tests

Documentation
------------

.. code-block:: bash

poetry build
pip3 install -U dist/musicbot-0.1.0-py3-none-any.whl
doc/gen.sh
