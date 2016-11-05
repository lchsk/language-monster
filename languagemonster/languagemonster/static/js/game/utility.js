function shuffle(array)
{
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

    for (var i = 0; i < array_1d.length - 1; i += 2) {
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

function getCookie(name)
{
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

MONSTER.Const = function() {};

MONSTER.Const.PI = 3.14159265359;
MONSTER.Const.PI_2 = MONSTER.Const.PI / 2.0;

MONSTER.Const.AHEAD = 1;
MONSTER.Const.LEFT = 2;
MONSTER.Const.RIGHT = 3;

// Fonts

MONSTER.Const.FONTS = {};

MONSTER.Const.DEFAULT_FONT_FAMILY = "Montserrat";

MONSTER.Const.COLOURS = {
    "navy": "#160E41",
    "white": "#ffffff"
};

MONSTER.initFonts = function(font_families, colours, sizes)
{
    var fonts = MONSTER.Const.FONTS;

    for (var i = 0; i < font_families.length; i++) {
        var font_family = font_families[i];

        fonts[font_family] = fonts[font_family] || {};

        for (var j = 0; j < colours.length; j++) {
            var colour = colours[j];

            fonts[font_family][colour] = fonts[font_family][colour] || {};

            for (var k = 0; k < sizes.length; k++) {
                var size = sizes[k];

                fonts[font_family][colour][size] = {
                    fontFamily: font_family,
                    fontSize: parseInt(size),
                    fill: colour
                };
            }
        }
    }
};

MONSTER.getFonts = function(font_family, colour)
{
    return MONSTER.Const.FONTS[font_family][colour];
};

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

MONSTER.Utils.to_radians = function(degrees) {
    return degrees * MONSTER.Const.PI / 180;
};

MONSTER.Utils.isPointInRect = function(x, y, rect) {
    return MONSTER.Utils.isPointInRectWithTol(x, y, rect, [0, 0]);
};

MONSTER.Utils.isPointInRectWithTol = function(x, y, rect, tolerance) {
    // x (number): X coordinate of a point
    // y (number): Y coordinate of a point
    // rect (array): An array with 4 items - x, y, width, height
    // tolerance (array): An array with 2 items - tolerance on X and Y axis.
    //                    0% tolerance is default

    var tol_x = tolerance[0] / 100.0 * rect[2];
    var tol_y = tolerance[1] / 100.0 * rect[3];

    return (
        x >= rect[0] - tol_x &&
        x <= rect[0] + rect[2] + tol_x &&
        y >= rect[1] - tol_y &&
        y <= rect[1] + rect[3] + tol_y
    );
};

MONSTER.Utils.getRandomInt = function(min, max) {
    // Returns a random integer between min (inclusive) and max (inclusive)

    return Math.floor(Math.random() * (max - min + 1)) + min;
};

MONSTER.Utils.clamp = function(value, min, max) {
    if (value <= min)
        return min;

    if (value >= max)
        return max;

    return value;
};

MONSTER.Utils.bezier = function(t, p) {
    var x = (1 - t) * (1 - t) * p[0].x + 2 * (1 - t) * t * p[1].x + t * t * p[2].x;
    var y = (1 - t) * (1 - t) * p[0].y + 2 * (1 - t) * t * p[1].y + t * t * p[2].y;

    return {
        'x': x,
        'y': y
    };
};
