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

  sudo apt install libtag1-dev ffmpeg postgresql-11 pgcli libpcre3-dev
  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3
  poetry install

  systemctl status postgresql
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

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload
