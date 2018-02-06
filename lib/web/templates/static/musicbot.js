$(document).ready(function() {
    console.log('After page load');
    shuffleParam = "shuffe=1";
    shuffleInput = 'input#shuffle';
    if (window.location.search.indexOf(shuffleParam) > -1) {
        $(shuffleInput).prop('checked', true);
    }

    $('a').click(function (event) {
        var href = this.href;
        var a = this;
        if($(shuffleInput).prop('checked')) {
            a.href = href + ((href.indexOf('?')!=-1)?'&':'?') + shuffleParam;
        }
    });
});
