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

Installation
------------

.. code-block:: bash

  sudo apt install libtag1-dev ffmpeg
  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot
  python-3.6 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
