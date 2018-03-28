$(document).ready(function () {
    var current = URI(window.location);
    var params = current.search(true);
    var audio;
    var playlist;
    var tracks;
    var current;

    init();

    function init() {
        current = 0;
        audio = $('#player');
        playlist = $('#playlist');
        tracks = playlist.find('li a');
        len = tracks.length - 1;

        // check volume
        volumeParam = "volume";
        if (params.hasOwnProperty(volumeParam)) {
            audio[0].volume = params[volumeParam] / 100;
        } else {
            audio[0].volume = 1;
        }

        // check autoplay
        autoplayParam = "autoplay";
        if (params.hasOwnProperty(autoplayParam)) {
            playPromise = audio[0].play();
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    console.log('Autoplay is ok.');
                })
                .catch(error => {
                    console.log('Autoplay issue.');
                });
            }
        }

        playlist.find('a').click(function (e) {
            e.preventDefault();
            link = $(this);
            current = link.parent().index();
            run(link, audio[0]);
        });
        audio[0].addEventListener('ended', function (e) {
            current++;
            if (current > len) {
                //current = 0;
                audio[0].pause()
                link = playlist.find('a')[0];
                console.log('Last song ended');
            } else {
                link = playlist.find('a')[current];
                run($(link), audio[0]);
            }
        });
    }
    function run(link, player) {
        player.src = link.attr('href');
        par = link.parent();
        par.addClass('active').siblings().removeClass('active');
        audio[0].load();
        var playPromise = audio[0].play();
        if (playPromise !== undefined) {
            playPromise.then(_ => {
                console.log('Autoplay is ok.');
            })
            .catch(error => {
                console.log('Autoplay issue.');
            });
        }
    }
})
function volumechanged(){
    console.log('Volume changed');
}
