$(document).ready(function () {
    var current = URI(window.location);
    var params = current.search(true);
    var audio;
    var playlist;
    var tracks;
    var current;
    var loop = false;

    init();

    function init() {
        current = 0;
        audio = $('#player');
        playlist = $('#playlist');
        tracks = playlist.find('li a');
        len = tracks.length - 1;

        var first = tracks.first();
        if (first){
            console.log('Setting title to'+first.text());
            document.title = first.text();
        }

        // check loop
        loopParam = "loop";
        if (params.hasOwnProperty(loopParam)) {
            console.log('Enable loop')
            loop = true;
        } else {
            console.log('Disable loop')
            loop = false;
        }

        // check volume
        volumeParam = "volume";
        if (params.hasOwnProperty(volumeParam)) {
            console.log('Custom volume')
            audio[0].volume = params[volumeParam] / 100;
        } else {
            console.log('Default volume')
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
                audio[0].pause()
                link = playlist.find('a')[0];
                console.log('Last song ended');
                if (loop) {
                    console.log('Loop enabled, return to first song');
                    current = 0;
                    link = playlist.find('a')[current];
                    run($(link), audio[0]);
                }
            } else {
                link = playlist.find('a')[current];
                run($(link), audio[0]);
            }
        });
    }
    function run(link, player) {
        player.src = link.attr('href');
        console.log('Setting title to'+link.text());
        document.title = link.text();
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
