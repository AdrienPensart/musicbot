/* eslint semi: ["error", "always"] */
/* global $, URI */
$(document).ready(function () {
  var currentUri = URI(window.location);
  var params = currentUri.search(true);
  var current = 0;
  var audio = $('#player');
  var playlist = $('#playlist');
  var tracks = playlist.find('li a');
  var loop = false;
  var len = tracks.length - 1;

  function run (link, player) {
    player.src = link.attr('href');
    console.log('Setting title to' + link.text());
    document.title = link.text();
    var par = link.parent();
    par.addClass('active').siblings().removeClass('active');
    audio[0].load();
    var playPromise = audio[0].play();
    if (playPromise !== undefined) {
      playPromise.then(_ => {
        console.log('Autoplay is ok');
      })
        .catch(error => {
          console.log('Autoplay issue: ', error);
        });
    }
  }

  var first = tracks.first();
  if (first) {
    console.log('Setting title to' + first.text());
    document.title = first.text();
  }

  // check loop
  var loopParam = 'loop';
  if (params.hasOwnProperty(loopParam)) {
    console.log('Enable loop');
    loop = true;
  } else {
    console.log('Disable loop');
    loop = false;
  }

  // check volume
  var volumeParam = 'volume';
  if (params.hasOwnProperty(volumeParam)) {
    console.log('Custom volume');
    audio[0].volume = params[volumeParam] / 100;
  } else {
    console.log('Default volume');
    audio[0].volume = 1;
  }

  // check autoplay
  var autoplayParam = 'autoplay';
  if (params.hasOwnProperty(autoplayParam)) {
    var playPromise = audio[0].play();
    if (playPromise !== undefined) {
      playPromise.then(_ => {
        console.log('Autoplay is ok.');
      })
        .catch(error => {
          console.log('Autoplay issue: ', error);
        });
    }
  }

  playlist.find('a').click(function (e) {
    e.preventDefault();
    var link = $(this);
    current = link.parent().index();
    run(link, audio[0]);
  });
  audio[0].addEventListener('ended', function (e) {
    current++;
    if (current > len) {
      audio[0].pause();
      console.log('Last song ended');
      if (loop) {
        console.log('Loop enabled, return to first song');
        current = 0;
        var link = playlist.find('a')[current];
        run($(link), audio[0]);
      }
    } else {
      var currentLink = playlist.find('a')[current];
      run($(currentLink), audio[0]);
    }
  });
});
