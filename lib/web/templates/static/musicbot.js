$(document).ready(function() {
    var current = URI(window.location);
    var params = current.search(true);

    // SHUFFLE
    shuffleParam = "shuffle";
    shuffleInput = 'input#shuffle';
    if (params.hasOwnProperty(shuffleParam)) {
        $(shuffleInput).prop('checked', params[shuffleParam]);
    }

    $(shuffleInput).change(function() {
        var current = URI(window.location);
        if (this.checked) {
            current.addSearch(shuffleParam, "1");
        } else {
            current.removeSearch(shuffleParam);
        }
        window.location = current.href();
    });

    // LIMIT
    limitParam = "limit";
    limitInput = "input#limit";
    if (params.hasOwnProperty(limitParam)) {
        $(limitInput).prop('value', params[limitParam])
    }

    $(limitInput).on('keyup change click', function() {
        var current = URI(window.location);
        var params = current.search(true);
        if (this.value != 0){
            if (params.hasOwnProperty(limitParam)){
                if (params[limitParam] == this.value){
                    return;
                }
            }
            current.setSearch(limitParam, this.value);
        } else {
            current.removeSearch(limitParam);
        }
        window.location = current.href();
    });

    // LINK BUILD
    $('a').on('click contextmenu', function (event) {
        var next = URI(this.href);
        var a = this;
        if($(shuffleInput).prop('checked')) {
            next.setSearch(shuffleParam, '1');
        }
        if($(limitParam).prop('value') != 0) {
            next.setSearch(limitParam, $(limitInput).prop('value'));
        }
        a.href = next.href();
    });

});
