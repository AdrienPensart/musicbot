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

It uses poetry tool to manage project life and docker to test it.

Dev Environment
------------

.. code-block:: bash

  sudo apt install -y vlc libtag1-dev postgresql-server-dev-all ffmpeg python3-pip docker.io libchromaprint-tools libbz2-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev tk-dev liblzma-dev libssl-dev libreadline-dev
  sudo usermod -aG docker $USER

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  https://pyenv.run | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  python <(curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py) --preview
  poetry install

Testing
------------

.. code-block:: bash

  poetry run pytest
  poetry run coverage-badge -f -o doc/coverage.svg

Docker
------------

.. code-block:: bash

  docker-compose build --parallel
  docker-compose up
  export MB_USER=test@test.com
  export MB_PASSWORD=password
  musicbot user create
  musicbot local scan /tests/fixtures/folder1 /tests/fixtures/folder2
  musicbot local tracks

Linting
------------

.. code-block:: bash

  poetry run pylint musicbot tests

Documentation
------------

.. code-block:: bash

  poetry build
  poetry run doc/gen.sh
