$(document).ready(function() {
    shuffleParam = "shuffle=1";
    shuffleInput = 'input#shuffle';
    if (window.location.search.indexOf(shuffleParam) > -1) {
        $(shuffleInput).prop('checked', true);
    }

    // limitParam = "limit=";
    // limitInput = "input#limit";
    // if (window.location.search.indexOf(limitParam) > -1) {
    //     $(limitInput).prop('value')
    // }

    $('a').on('click contextmenu', function (event) {
        var href = this.href;
        var a = this;
        if($(shuffleInput).prop('checked')) {
            a.href = href + ((href.indexOf('?')!=-1)?'&':'?') + shuffleParam;
        }
    });
});
