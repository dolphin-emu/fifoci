function getImageData(image) {
  // a modified version of toImageDataFromImage
  // that uses naturalHeight/Width when possible
  var
    height = image.naturalHeight || image.height,
    width = image.naturalWidth || image.width;
  var canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  var context = canvas.getContext('2d');
  context.clearRect(0, 0, width, height);
  context.drawImage(image, 0, 0, width, height);
  return context.getImageData(0, 0, width, height);
}

function make_diff(img_id_a, img_id_b, diff_id) {
  function getImageDataByID(id) {
    return getImageData(document.getElementById(id));
  }
  var img_a = document.getElementById(img_id_a),
      img_b = document.getElementById(img_id_b),
      diff_container = document.getElementById(diff_id);
  if (!(img_a && img_b && diff_container))
    return;

  if (img_a.src === img_b.src) {
    diff_container.innerHTML = 'identical output';
    return;
  }

  var diff = imagediff.diff(getImageData(img_a), getImageData(img_b));
  var canvas = imagediff.createCanvas(diff.width, diff.height);
  context = canvas.getContext('2d');
  context.putImageData(diff, 0, 0);
  diff_container.innerHTML = (
    '<img class="img-diff" src="' + canvas.toDataURL("image/png") + '">' +
    '<img class="img-a" src="' + img_a.src + '">' +
    '<img class="img-b" src="' + img_b.src + '">'
  );
}

$(window).load(function() {
  var i = 0;
  while (1) {
    var el = document.getElementById("res-" + i + "-a");
    if (!el)
      break;
    make_diff("res-" + i + "-a", "res-" + i + "-b", "res-" + i + "-diff");
    i++;
  }

  $(".img-a, .img-b").hide();

  $('#diff-ui-bright').click(function() {
    var b = 1000;
    $('.img-a, .img-b').hide();
    $('.img-diff').show().css({'filter': 'brightness(' + b + ')',
                               '-webkit-filter': 'brightness(' + b + ')'});
  });
  $('#diff-ui-diff').click(function() {
    $('.img-a, .img-b').hide();
    $('.img-diff').show().css({'filter': '', '-webkit-filter': ''});
  });
  $('#diff-ui-left').click(function() {
    $('.img-diff, .img-b').hide();
    $('.img-a').show();
  });
  $('#diff-ui-right').click(function() {
    $('.img-diff, .img-a').hide();
    $('.img-b').show();
  });

  $(document).keydown(function (e) {
    $({
      49: '#diff-ui-diff',   // 1
      50: '#diff-ui-bright', // 2
      51: '#diff-ui-left',   // 3
      52: '#diff-ui-right'   // 4
    }[e.which]).click();
  });

  // Enable the keyboard shortcut tooltips.
  $('[data-toggle="tooltip"]').tooltip({container: 'body'})
})
