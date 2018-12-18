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

  sudo apt install build-essential libssl-dev libtag1-dev ffmpeg postgresql-11 libpcre3-dev postgresql-server-dev-all
  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3
  poetry install

  echo "shared_preload_libraries = 'pg_stat_statements'" >> /etc/postgresql/11/main/postgresql.conf
  echo "pg_stat_statements.track = all" >> /etc/postgresql/11/main/postgresql.conf
  systemctl restart postgresql
  sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'musicbot';" && history -c
  poetry run pgcli postgresql://postgres:musicbot@localhost:5432

  git clone https://github.com/nginx/nginx.git
  git clone https://github.com/evanmiller/mod_zip.git
  auto/configure --prefix=/opt/nginx --add-module="$HOME/mod_zip"
  sudo make install
  sudo ln -s /home/crunch/musicbot/scripts/musicbot.service /etc/systemd/system/musicbot.service
  sudo ln -s /home/crunch/musicbot/scripts/nginx.service /etc/systemd/system/nginx.service
  sudo ln -s /home/crunch/musicbot/scripts/nginx.conf /opt/nginx/conf/nginx.conf
  sudo ln -s /opt/nginx/sbin/nginx /usr/sbin/nginx

  git clone https://github.com/michelp/pgjwt.git
  cd pgjwt
  sudo make install

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload

  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
  nvm install node
  curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
  echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
  sudo apt-get update && sudo apt-get install --no-install-recommends yarn
  yarn add postgraphile
  yarn add postgraphile-plugin-connection-filter
