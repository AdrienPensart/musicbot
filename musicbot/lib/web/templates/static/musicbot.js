/* eslint semi: ["error", "always"] */
/* global $, URI */
$(document).ready(function () {
  var current = URI(window.location);
  var params = current.search(true);

  // SHUFFLE
  var shuffleParam = 'shuffle';
  var shuffleInput = 'input#shuffle';
  if (params.hasOwnProperty(shuffleParam)) {
    $(shuffleInput).prop('checked', params[shuffleParam]);
  }

  $(shuffleInput).change(function () {
    var current = URI(window.location);
    if (this.checked) {
      current.addSearch(shuffleParam, '1');
    } else {
      current.removeSearch(shuffleParam);
    }
    window.location = current.href();
  });

  // LOOP
  var loopParam = 'loop';
  var loopInput = 'input#loop';
  if (params.hasOwnProperty(loopParam)) {
    $(loopInput).prop('checked', params[loopParam]);
  }

  $(loopInput).change(function () {
    var current = URI(window.location);
    if (this.checked) {
      current.addSearch(loopParam, '1');
    } else {
      current.removeSearch(loopParam);
    }
    window.location = current.href();
  });

  // AUTOPLAY
  var autoplayParam = 'autoplay';
  var autoplayInput = 'input#autoplay';
  if (params.hasOwnProperty(autoplayParam)) {
    $(autoplayInput).prop('checked', params[autoplayParam]);
  }

  $(autoplayInput).change(function () {
    var current = URI(window.location);
    if (this.checked) {
      current.addSearch(autoplayParam, '1');
    } else {
      current.removeSearch(autoplayParam);
    }
    window.location = current.href();
  });

  // EXCLUDE LIVES
  var noKeywordsParam = 'no_keywords';
  var excludeLivesInput = 'input#lives';
  if (params.hasOwnProperty(noKeywordsParam)) {
    $(excludeLivesInput).prop('checked', params[noKeywordsParam].includes('live'));
  }

  $(excludeLivesInput).change(function () {
    var current = URI(window.location);
    if (this.checked) {
      current.addSearch(noKeywordsParam, 'live');
    } else {
      current.removeSearch(noKeywordsParam);
    }
    window.location = current.href();
  });

  // LIMIT
  var limitParam = 'limit';
  var limitInput = 'input#limit';
  if (params.hasOwnProperty(limitParam) && params[limitParam].length) {
    $(limitInput).prop('value', params[limitParam]);
  }

  $(limitInput).on('change', function () {
    var current = URI(window.location);
    var params = current.search(true);
    if (this.value !== 0) {
      if (params.hasOwnProperty(limitParam)) {
        if (params[limitParam] === this.value) {
          return;
        }
      }
      current.setSearch(limitParam, this.value);
    } else {
      current.removeSearch(limitParam);
    }
    window.location = current.href();
  });

  // VOLUME
  var volumeParam = 'volume';
  var volumeInput = 'input#volume';
  if (params.hasOwnProperty(volumeParam) && params[volumeParam].length) {
    $(volumeInput).prop('value', params[volumeParam]);
  }

  $(volumeInput).on('change', function () {
    var current = URI(window.location);
    var params = current.search(true);
    if (this.value !== 0) {
      if (params.hasOwnProperty(volumeParam)) {
        if (params[volumeParam] === this.value) {
          return;
        }
      }
      current.setSearch(volumeParam, this.value);
    } else {
      current.removeSearch(volumeParam);
    }
    window.location = current.href();
  });

  // LINK BUILD
  $('a').on('click contextmenu', function (event) {
    var next = URI(this.href);
    var a = this;
    if ($(shuffleInput).prop('checked')) {
      next.setSearch(shuffleParam, '1');
    }
    if ($(autoplayInput).prop('checked')) {
      next.setSearch(autoplayParam, '1');
    }
    if (params.hasOwnProperty(limitParam) && params[limitParam].length && $(limitParam).prop('value') !== 0) {
      next.setSearch(limitParam, $(limitInput).prop('value'));
    }
    if (params.hasOwnProperty(volumeParam) && params[volumeParam].length && $(volumeParam).prop('value') !== 0) {
      next.setSearch(volumeParam, $(volumeInput).prop('value'));
    }
    a.href = next.href();
  });
});
