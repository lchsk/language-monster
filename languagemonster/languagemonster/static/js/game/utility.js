function shuffle(array) {
  var m = array.length, t, i;

  while (m) {
    i = Math.floor(Math.random() * m--);

    t = array[m];
    array[m] = array[i];
    array[i] = t;
  }

  return array;
}

// Converts 1-dimensional array, eg. [dog, perro, cat, gato]
// to 2-dimensional, eg. [[dog, perro], [cat, cato]]
function convertTo2D(array_1d)
{
  // input array must have even number of elements
  if (array_1d.length % 2 !== 0) return false;

  var ret = [];

  for (var i = 0; i < array_1d.length - 1; i += 2)
  {
    var e1 = array_1d[i];
    var e2 = array_1d[i + 1];
    var tmp = [e1, e2];
    ret.push(tmp);
  }

  return ret;
}

function objectValues(obj)
{
    var result = [];

    for (var key in obj)
    {
        if (obj.hasOwnProperty(key))
        {
            result.push(obj[key]);
        }
    }

    return result;
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

MONSTER.Const = function()
{
};

MONSTER.Const.PI = 3.14159265359;
MONSTER.Const.PI_2 = MONSTER.Const.PI / 2.0;

MONSTER.Const.AHEAD = 1;
MONSTER.Const.LEFT = 2;
MONSTER.Const.RIGHT = 3;

MONSTER.isZero = function(x)
{
    if (Math.abs(x) < 0.000001)
        return true;
    else
        return false;
};
MONSTER.linear = function(x, x_min, x_max, y_min, y_max)
{
    return (x / (x_max - x_min)) * (y_max - y_min) + y_min;
};

MONSTER.Utils = function() {
};

// Change character in a string given an index
MONSTER.Utils.replace_at = function(string, index, character) {
    return string.substr(0, index) + character + string.substr(index + character.length);
};


