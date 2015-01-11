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
  var image = new Image();
  image.src = canvas.toDataURL("image/png");
  diff_container.innerHTML = '';
  diff_container.appendChild(image);
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
})
