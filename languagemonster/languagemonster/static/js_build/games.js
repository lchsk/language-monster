var MONSTER = MONSTER || {};

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

MONSTER.Utils = function() {};

MONSTER.Utils.objectValues = function(obj)
{
    var result = [];

    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            result.push(obj[key]);
        }
    }

    return result;
};

MONSTER.Utils.shuffle = function(array)
{
    var m = array.length, t, i;

    while (m) {
        i = Math.floor(Math.random() * m--);

        t = array[m];
        array[m] = array[i];
        array[i] = t;
    }

    return array;
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

MONSTER.Common = function(){};

// MONSTER.Common.restart = function(obj)
// {

// };

MONSTER.Common.correct = function(game_screen)
{
    game_screen.game.learned.push(game_screen.current_pair.id);

    // Add points only if the question was asked the first time
    if (game_screen.game.round_id <= game_screen.game.actual_rounds) {
        game_screen.game.points++;
    }

    game_screen.resultScreen(true);
};

MONSTER.Common.negative = function(game_screen)
{
    game_screen.game.to_repeat.push(game_screen.current_pair.id);

    game_screen.game.to_ask.push(game_screen.current_pair);

    game_screen.resultScreen(false);
};

MONSTER.Common.check_answer = function(game, answer)
{
    if (answer === game.answer)
        MONSTER.Common.correct(answer);
    else
        MONSTER.Common.negative(answer);
};

MONSTER.Common._next_level = function(game)
{
    // Advance to the next level
    game.level_id++;
    game.next_level();
    game.kick_off();
};

MONSTER.Common.keyup_handler = function(event, game)
{
    if (event.keyCode === MONSTER.Key.ENTER) {
        document.removeEventListener('keyup', MONSTER.Common._continue_handler);
        delete MONSTER.Common._continue_handler;

        MONSTER.Common._next_level(game);
    }
};

MONSTER.Common.endScreen = function(obj)
{
    // End Level Screen (showing results)

    var context = obj;
    obj.game.view.removeChildren();

    var anon_game = obj.game.anon_game;

    var sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    var star_t = PIXI.Texture.fromImage(obj.game.assets.ui.ui_star);
    var dark_star_t = PIXI.Texture.fromImage(obj.game.assets.ui.ui_dark_star);

    obj.game.pct = Math.round(obj.game.points / obj.game.all.length * 100);

    var stars_cnt = obj.game.pct >= 75 ? 3 : obj.game.pct >= 45 ? 2 : 1;

    var stars = [];

    var i = 0;

    for (i = 0; i < stars_cnt; i++) {
        stars.push(new PIXI.Sprite(star_t));
    }

    for (i = stars.length; i < 3; i++) {
        stars.push(new PIXI.Sprite(dark_star_t));
    }

    var comment = new PIXI.Text("", sizes['30']);
    comment.text = MONSTER.Common.trans("Well done", window.translations);
    comment.position.x = (obj.game.width - comment.width) / 2;
    comment.position.y = 0.15 * obj.game.height;

    obj.game.view.addChild(comment);

    if (! anon_game) {
        obj.info = new PIXI.Text(
            MONSTER.Common.trans(
                "Sending results...",
                window.translations
            ),
            sizes['16']
        );
        obj.info.position.x = (obj.game.width - obj.info.width) / 2;
        obj.info.position.y = 0.89 * obj.game.height;

        obj.game.view.addChild(obj.info);
    }

    obj.b = MONSTER.Common.createButton(
        context,
        MONSTER.Common.trans(
            'Continue',
            window.translations
        ),
        0,
        0,
        200,
        100,
        (obj.game.width - 200) / 2,
        0.6 * obj.game.height,
        function() {
            MONSTER.Common._next_level(obj.game);
        }
    );

    var stars_box = new PIXI.Container();

    var star_w = stars[0].width + Math.round(stars[0].height * 0.1);

    for (i = 0; i < stars.length; i++) {
        stars[i].position.x = i * star_w;

        stars_box.addChild(stars[i]);
    }

    // Move edge stars a bit downwards
    stars[0].position.y = stars[2].position.y = stars[0].position.y
        += Math.round(0.25 * stars[0].height);

    stars_box.position.x = (obj.game.width - (star_w * 3)) / 2;
    stars_box.position.y = Math.round(0.28 * obj.game.height);
    obj.game.view.addChild(stars_box);

    if (anon_game)
        MONSTER.Common._activate_button(obj, obj.b);
    else
        MONSTER.Common.sendResults(obj);
};

MONSTER.Common.cancelAnimationFrame = function(id)
{
    var func = window.cancelAnimationFrame ||
        window.webkitCancelRequestAnimationFrame ||
        window.webkitCancelAnimationFrame ||
        window.mozCancelRequestAnimationFrame || window.mozCancelAnimationFrame ||
        window.oCancelRequestAnimationFrame || window.oCancelAnimationFrame ||
        window.msCancelRequestAnimationFrame || window.msCancelAnimationFrame;

    return func(id);
};

MONSTER.Common.getWordSet = function(game_screen)
{
    var game = game_screen.game;

    if (game.round_id === game.to_ask.length) {
        return false;
    }

    var pair = game.to_ask[game.round_id];
    game.round_id++;

    var dir_q = 0;
    var dir_a = 1;

    game_screen.current_pair = pair;
    game_screen.question = pair.words[dir_q];
    game_screen.answer = pair.words[dir_a];

    game_screen.choices = [];
    game_screen.choices.push(game_screen.answer);

    // TODO: Check if it makes a difference
    MONSTER.Utils.shuffle(game.all);

    for (var i = 0; i < game.all.length; i++) {
        if (game.all[i].id != game_screen.current_pair.id) {
            game_screen.choices.push(game.all[i].words[dir_a]);
        }

        if (game_screen.choices.length == 4) {
            break;
        }
    }

    game_screen.choices = MONSTER.Utils.shuffle(game_screen.choices);

    if (game_screen.choices.length != 4) {
        throw "Not enough choices";
    }

    return true;
};

MONSTER.Common.getLoader = function()
{
    var loader = PIXI.loader;
    loader.reset();

    return loader;
};

MONSTER.Common.showTutorial = function(game)
{
    if ( ! game.currentScreen)
        return;

    var played = window.games_played;
    var game_id = game.currentScreen.ID;

    if (played.indexOf(game_id) < 0)
    {
        played.push(game_id);
        MONSTER.Common._showTutorial(game, game.tutorial);
    }
};

MONSTER.Common._showTutorial = function(game, tutorial)
{
    $('#' + tutorial).modal('show');
    game.pause = true;
    game.currentScreen.onGamePause();
};

MONSTER.Common.hideCursor = function()
{
    document.body.style.cursor = 'none';
};

MONSTER.Common.showCursor = function()
{
    document.body.style.cursor = 'default';
};

MONSTER.Common.addUI = function(game)
{
    var btn_info = PIXI.Sprite.fromImage(game.assets.ui.ui_btn_info);
    btn_info.scale.x = btn_info.scale.y = 0.65;
    btn_info.interactive = true;

    var btn_menu = PIXI.Sprite.fromImage(game.assets.ui.ui_btn_menu);
    btn_menu.scale.x = btn_menu.scale.y = 0.65;
    btn_menu.interactive = true;
    btn_menu.position.x = 34;
    btn_menu.position.y = 2;

    if ( ! game.currentScreen)
        return;

    var tutorial_id = game.tutorial;

    btn_info.click = function() {
        MONSTER.Common._showTutorial(game, tutorial_id);
    };

    btn_info.mouseover = function() {
        document.body.style.cursor = 'pointer';
    };

    btn_info.mouseout = function() {
        document.body.style.cursor = 'default';
    };

    btn_menu.click = function() {
        location.reload();
    };

    btn_menu.mouseover = function() {
        document.body.style.cursor = 'pointer';
    };

    btn_menu.mouseout = function() {
        document.body.style.cursor = 'default';
    };

    $('#' + tutorial_id).on('hide.bs.modal', function(){
        game.pause = false;
        game.currentScreen.onGamePauseOff();
    });

    game.view.addChild(btn_info);
    game.view.addChild(btn_menu);
};

MONSTER.Common.getAnswersMinusCurrent = function(answers, current) {
    // Returns an array with answers without the one being clicked on

    var resp = [];

    for (var i = 0; i < answers.length; i++) {
        if (answers[i].text.text !== current.text.text)
            resp.push(answers[i]);
    }

    return resp;
};

MONSTER.Common.fillBackground = function(obj, color)
{
    obj.game.background.beginFill(color, 1);
    obj.game.background.drawRect(0, 0, obj.game.width, obj.game.height);
    obj.game.background.endFill();
};

MONSTER.Common.getCookie = function(name)
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
};

MONSTER.Common.setUpAjax = function()
{
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url)
                  || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader(
                    "X-CSRFToken",
                    MONSTER.Common.getCookie('csrftoken')
                );
            }
        }
    });
};

MONSTER.Common.secure_answer_size = function(text_obj, sizes, max_size)
{
    // Used in games (for answers not buttons)

    // Number of characters that launches an attempt to split text
    // into several lines
    var chars_to_break = 18;
    var len = text_obj.text.length;

    if (text_obj.text.indexOf(' ') != -1 && len > chars_to_break) {
        var breaks_cnt = Math.floor(len / chars_to_break);

        // Number of characters in a line between a break
        var continous_len = Math.floor(0.66 * chars_to_break);
        var last_break_idx = 0;

        if (breaks_cnt > 0) {
            for (var i = 0; i < len; i++) {
                if (text_obj.text[i] == ' '
                    && (i - last_break_idx > continous_len)) {
                    last_break_idx = i;
                    text_obj.text = MONSTER.Utils.replace_at(
                        text_obj.text, i, '\n');
                    breaks_cnt--;
                }

                if (breaks_cnt === 0) {
                    break;
                }
            }
        }
    }

    for (var j = 0; j < sizes.length; j++) {
        text_obj.style = sizes[j];

        if (text_obj.width <= max_size) {
            break;
        }
    }
};

MONSTER.Common.createButton = function(
    context,
    t,
    x,
    y,
    width,
    height,
    plane_x,
    plane_y,
    onclick
) {
    var b = new PIXI.Graphics();
    b.position.x = plane_x;
    b.position.y = plane_y;

    b.beginFill(context.button_colors.active);
    b.drawRect(x, y, width, height);
    b.endFill();

    b.interactive = false;
    b.hitArea = new PIXI.Rectangle(x, y, width, height);
    b.text = t;

    var all_sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    var sizes = [
        all_sizes['26'],
        all_sizes['22'],
        all_sizes['16'],
        all_sizes['12']
    ];
    var text = new PIXI.Text(t, sizes[0]);

    var secureSize = function(max_size) {
        for (var i = 0; i < sizes.length; i++) {
            text.style = sizes[i];
            text.position.x = x + (width - text.width) / 2;
            text.position.y = y + (height - text.height) / 2 + 2;

            if (text.width <= max_size) {
                break;
            }
        }
    };

    secureSize(width);
    b.addChild(text);

    b.click = function()
    {
        b.clear();
        b.beginFill(context.button_colors.click);
        b.drawRect(x, y, width, height, 3);
        b.endFill();
        onclick();
    };

    b.mouseover = function()
    {
        b.clear();
        b.beginFill(context.button_colors.hover);
        b.drawRect(x, y, width, height, 3);
        b.endFill();
        document.body.style.cursor = 'pointer';
    };

    b.mouseout = function()
    {
        b.clear();
        b.beginFill(context.button_colors.active);
        b.drawRect(x, y, width, height, 3);
        b.endFill();

        document.body.style.cursor = 'default';
    };

    return b;
};

MONSTER.Common.sendResults = function(obj)
{
    $.ajax({
        method: "POST",
        crossDomain: false,
        url: "/api/local/users/results",
        contentType: "application/json",
        data: JSON.stringify(
            {
                dataset_id: obj.game.data.dataset_id,
                email: obj.game.data.email,
                mark: obj.game.pct,
                words_learned: obj.game.learned,
                to_repeat: obj.game.to_repeat,
                game: obj.ID
            }),
        dataType: "json"
    }).success(function() {
        obj.info.text = MONSTER.Common.trans(
            "Results were sent",
            window.translations);
        obj.info.position.x = (obj.game.width - obj.info.width) / 2;

        // Go on to the next level with <enter>
        MONSTER.Common._continue_handler = function(event) {
            MONSTER.Common.keyup_handler(event, obj.game);
        };

        document.addEventListener('keyup', MONSTER.Common._continue_handler,
                                  false);

        MONSTER.Common._activate_button(obj, obj.b);

    }).error(function() {
        obj.info.text = MONSTER.Common.trans(
            "Error when sending results",
            window.translations);
        obj.info.position.x = (obj.game.width - obj.info.width) / 2;
    });
};

MONSTER.Common._activate_button = function(context, button)
{
    context.game.view.addChild(button);
    button.interactive = true;
};

MONSTER.Common.trans = function(word, d)
{
    if (word in d)
        return d[word];
    return word;
};

MONSTER.Common.parallax = function(delta, parallax_array, parallax_speed, width)
{
    for (var i = 0; i < parallax_array.length; i++) {
        var sprites = parallax_array[i];
        var speed = parallax_speed[i];

        for (var j = 0; j < sprites.length; j++) {
            var bg = sprites[j];

            // bg.position.x -= Math.round(speed * delta);
            bg.position.x -= speed * delta;

            if (bg.position.x <= -width) {
                var shifted_bg = sprites.shift();

                shifted_bg.position.x = width;

                sprites.push(shifted_bg);
            }
        }
    }
};

MONSTER.GoodWrongScreen = function(game, result_screen_x, result_screen_pos)
{
    var box = new PIXI.Container();
    var pos_screen = new PIXI.Graphics();
    pos_screen.beginFill(0xffffff, 0.8);
    pos_screen.drawRect(
        result_screen_x.show,
        result_screen_pos.y,
        result_screen_pos.width,
        result_screen_pos.height
    );
    pos_screen.endFill();

    var sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    var pos_screen_comment = new PIXI.Text("", sizes['30']);
    var pos_screen_text = new PIXI.Text("", sizes['36']);

    // We need to create alternative way to show good/wrong word pair.
    // When word pair does not fit into a single line, we put it in three
    // text objects, base, '=', and target.

    var pos_screen_text_line1 = new PIXI.Text("", sizes['30']);
    var pos_screen_text_line2 = new PIXI.Text("", sizes['30']);
    var pos_screen_text_line3 = new PIXI.Text("", sizes['30']);

    pos_screen_text.position.y = (game.height - pos_screen_text.height) / 2;
    pos_screen_comment.position.y = (game.height - pos_screen_comment.height) / 4;

    box.addChild(pos_screen);
    pos_screen.addChild(pos_screen_text);
    pos_screen.addChild(pos_screen_comment);
    pos_screen.addChild(pos_screen_text_line1);
    pos_screen.addChild(pos_screen_text_line2);
    pos_screen.addChild(pos_screen_text_line3);

    return {
        box: box,
        pos_screen: pos_screen,
        pos_screen_comment: pos_screen_comment,
        pos_screen_text: pos_screen_text,
        pos_screen_text_line1: pos_screen_text_line1,
        pos_screen_text_line2: pos_screen_text_line2,
        pos_screen_text_line3: pos_screen_text_line3
    };
};

MONSTER.GoodWrongScreen.prepare = function(game_screen, is_correct) {
    var box = game_screen.box;

    box.pos_screen_text.text = game_screen.question + ' = ' + game_screen.answer;

    if (box.pos_screen_text.width > 0.8 * game_screen.game.width) {
        box.pos_screen_text.text = '';
        box.pos_screen_text_line1.text = game_screen.question;
        box.pos_screen_text_line2.text = '=';
        box.pos_screen_text_line3.text = game_screen.answer;

        box.pos_screen_text_line1.position.x = (
            game_screen.game.width - box.pos_screen_text_line1.width
        ) / 2;
        box.pos_screen_text_line2.position.x = (
            game_screen.game.width - box.pos_screen_text_line2.width
        ) / 2;
        box.pos_screen_text_line3.position.x = (
            game_screen.game.width - box.pos_screen_text_line3.width
        ) / 2;

        box.pos_screen_text_line1.position.y = (
            game_screen.game.height - box.pos_screen_text_line1.height
        ) / 2;
        box.pos_screen_text_line2.position.y = box.pos_screen_text_line1.position.y +
            box.pos_screen_text_line2.height;

        box.pos_screen_text_line3.position.y = box.pos_screen_text_line2.position.y +
            box.pos_screen_text_line3.height;
    } else {
        // Fits in a single line

        box.pos_screen_text_line1.text = '';
        box.pos_screen_text_line2.text = '';
        box.pos_screen_text_line3.text = '';
        box.pos_screen_text.position.x = (
            game_screen.game.width - box.pos_screen_text.width
        ) / 2;
    }

    var comment = is_correct
            ? MONSTER.Common.trans('Good', game_screen.trans)
            : MONSTER.Common.trans('Wrong', game_screen.trans);
    box.pos_screen.tint = is_correct ?
        game_screen.colors.success
        : game_screen.colors.failure;

    box.pos_screen_comment.text = comment;
    box.pos_screen_comment.position.x =
        (game_screen.game.width - box.pos_screen_comment.width) / 2;

    box.box.position.x = game_screen.result_screen_x.right;

    game_screen.game.tweens.push(
        new MONSTER.Tween(
            box.box,
            'position.x',
            game_screen.result_screen_x.show,
            1000
        )
    );

    game_screen.game.setStopFunc(game_screen.next_round, 2000, game_screen);
};

MONSTER.Easing = function()
{

};

MONSTER.Easing.prototype.constructor = MONSTER.Easing;

MONSTER.Easing.linear = function(t){ return t; };
MONSTER.Easing.easeInQuad = function(t){ return t*t; };
MONSTER.Easing.easeOutQuad = function(t){ return t*(2-t); };
MONSTER.Easing.easeInOutQuad = function(t){ return t<0.5 ? 2*t*t : -1+(4-2*t)*t; };
MONSTER.Easing.easeInCubic = function(t){ return t*t*t; };
MONSTER.Easing.easeOutCubic = function(t){ return (--t)*t*t+1; };
MONSTER.Easing.easeInOutCubic = function(t){ return t<0.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1; };
MONSTER.Easing.easeInQuart = function(t){ return t*t*t*t; };
MONSTER.Easing.easeOutQuart = function(t){ return 1-(--t)*t*t*t; };
MONSTER.Easing.easeInOutQuart = function(t){ return t<0.5 ? 8*t*t*t*t : 1-8*(--t)*t*t*t; };
MONSTER.Easing.easeInQuint = function(t){ return t*t*t*t*t; };
MONSTER.Easing.easeOutQuint = function(t){ return 1+(--t)*t*t*t*t; };
MONSTER.Easing.easeInOutQuint = function(t){ return t<0.5 ? 16*t*t*t*t*t : 1+16*(--t)*t*t*t*t; };

function setData(obj, key, val)
{
    var ka = key.split(/\./);

    if (ka.length < 2) {
        obj[ka[0]] = val;
    } else {
        if (!obj[ka[0]])
            obj[ka[0]] = {};

        obj = obj[ka.shift()];

        setData(obj, ka.join("."), val);
    }
}

function getData(obj, key)
{
    var ka = key.split(/\./);

    if (ka.length < 2) {
        return obj[ka[0]];
    } else {
        if (!obj[ka[0]])
            obj[ka[0]] = {};
        obj = obj[ka.shift()];

        return getData(obj, ka.join("."));
    }
}

MONSTER.Tween = function(object, variable, targetValue, time)
{
    this.object = object;
    this.variable = variable;
    this.targetValue = targetValue;
    this.time = time;
    this.currentTime = 0;

    this.startValue = getData(this.object, this.variable);

    this.active = true;
};

MONSTER.Tween.prototype.update = function(t)
{
    this.currentTime += t;
    var pct = this.currentTime / this.time;
    var ft = MONSTER.Easing.easeOutCubic(pct);

    var val = Math.round(ft * (this.targetValue - this.startValue)) + this.startValue;

    if (this.active) {
        setData(this.object, this.variable, val);
    }

    if (this.currentTime > this.time) {
        this.active = false;
    }
};

MONSTER.FuncTimer = function(func, time)
{
    this.func = func;
    this.time = time;
    this.currentTime = 0;

    this.active = true;
};

MONSTER.FuncTimer.prototype.update = function(t)
{
    if (! this.active)
        return;

    this.currentTime += t;

    if (this.active && this.currentTime > this.time) {
        this.active = false;
        this.func();
    }
};


// Adapted from:
// http://nokarma.org/2011/02/27/javascript-game-development-keyboard-input/

MONSTER.Key = function()
{
};

MONSTER.Key._pressed = {};

MONSTER.Key.P = 80;
MONSTER.Key.SPACE = 32;
MONSTER.Key.ENTER = 13;
MONSTER.Key.LEFT = 37;
MONSTER.Key.UP = 38;
MONSTER.Key.RIGHT = 39;
MONSTER.Key.DOWN = 40;

MONSTER.Key.isDown = function(keyCode)
{
    return MONSTER.Key._pressed[keyCode];
};

MONSTER.Key.isUp = function(keyCode)
{
    if (MONSTER.Key._pressed[keyCode]) {
        delete MONSTER.Key._pressed[keyCode];

        return true;
    }

    return false;
};

MONSTER.Key.onKeydown = function(event)
{
    MONSTER.Key._pressed[event.keyCode] = true;
};

MONSTER.Key.onKeyup = function(event)
{
    delete MONSTER.Key._pressed[event.keyCode];
};

window.addEventListener('keyup', function(event) {
    MONSTER.Key.onKeyup(event);
}, false);
window.addEventListener('keydown', function(event) {
    MONSTER.Key.onKeydown(event);
}, false);

MONSTER.Key.blockScrolling = function()
{
    window.addEventListener("keydown", function(e){
        if([
            MONSTER.Key.SPACE,
            MONSTER.Key.LEFT,
            MONSTER.Key.RIGHT,
            MONSTER.Key.DOWN,
            MONSTER.Key.UP
        ].indexOf(e.keyCode) > -1) {
            e.preventDefault();
        }
    }, false);
};

MONSTER.DataLoader = function(
    dataset_id,
    email,
    max_rounds,
    success_func,
    anon_game,
    sender
)
{
    this.dataset_id = dataset_id;
    this.email = email;
    this.max_rounds = max_rounds;
    this.pack = {};
    this.success = false;
    this.success_func = success_func;
    this.sender = sender;
    this.anon_game = anon_game;
};

MONSTER.DataLoader.prototype.constructor = MONSTER.DataLoader;

// Basic way to load stuff
// Words in base and target languages (pairs)
MONSTER.DataLoader.prototype.loadWordPairs = function()
{
    var that = this;
    that.success = false;
    that.error_code = null;

    var url = "/api/local/words/" + this.dataset_id;

    // Anonymous player
    if (! this.anon_game)
        url += "/" + this.email;

    $.ajax({
        method: "GET",
        crossDomain: false,
        timeout: 15000,
        url: url,
        error: function(x, t) {
            that.success = false;
            that.error_code = t;

            var error_text = MONSTER.Common.trans(
                "Server error, please try again",
                window.translations
            ) + " (" + t + ")";
            that.sender.top_bar_loading_text.text = error_text;
            var new_x = (
                0.5 * that.sender.game.width - 0.5
                * that.sender.top_bar_loading_text.width
            );
            that.sender.top_bar_loading_text.position.x = new_x;

            var b1 = MONSTER.Common.createButton(
                that.sender,
                MONSTER.Common.trans(
                    "Try again",
                    window.translations
                ),
                0,
                0,
                200,
                50,
                300,
                360,
                function() {
                    location.href = window.location.href;
                }
            );
            b1.interactive = true;
            that.sender.game.view.addChild(b1);
        },
        success: function(m) {
            that.word_sets = m;
            that.success = true;

            that.success_func.apply(that.sender, [that.sender]);
        }
    });
};

MONSTER.AbstractScreen = function(game)
{
    this.game = game;
};

MONSTER.AbstractScreen.prototype.constructor = MONSTER.AbstractScreen;


MONSTER.AbstractScreen.prototype.update = function()
{
    if (this.game.DEBUG) {
        var debug = this.game.debug;

        debug['fps_ticks']++;
        debug['fps_timer'] += Math.round(1000 / this.game.timeSinceLastFrame);

        if (debug['fps_timer'] >= 1000) {
            debug['fps'] = Math.round(debug['fps_timer'] / debug['fps_ticks']);
            debug['fps_timer'] = 0;
            debug['fps_ticks'] = 1;
        }

        debug['fps_text'].text = debug['fps'];
    }
};

MONSTER.LoadingScreen = function(game)
{
    var that = this;
    this.game = game;
    this.ID = 'loader';

    MONSTER.AbstractScreen.call(this, game);
    MONSTER.Key.blockScrolling();

    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------
    this.colors = {
        background: '0x76D3DE',

        success: '0x33E46D',
        failure: '0xFF5039'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    MONSTER.Common.setUpAjax();

    this.game.anon_game = ! this.game.data.email;

    this.data_loader = new MONSTER.DataLoader(
        this.game.data.dataset_id,
        this.game.data.email,
        this.max_rounds,
        this.start_loading,
        this.game.anon_game,
        this
    );

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0, 0, this.game.width, this.game.height
    );

    this.box = new PIXI.Container();
    this.pos_screen = new PIXI.Graphics();
    this.pos_screen.beginFill(0xffffff, 0.8);
    this.pos_screen.drawRect(
        this.result_screen_x.show,
        this.result_screen_pos.y,
        this.result_screen_pos.width,
        this.result_screen_pos.height
    );
    this.pos_screen.endFill();

    this.pos_screen_comment = new PIXI.Text("", this.sizes['30']);
    this.pos_screen_text = new PIXI.Text("Language Monster", this.sizes['36']);

    this.pos_screen_text.position.y =
        (this.game.height - this.pos_screen_text.height) / 2;
    this.pos_screen_comment.position.y =
        (this.game.height - this.pos_screen_comment.height) / 4;

    this.box.addChild(this.pos_screen);
    this.pos_screen.addChild(this.pos_screen_text);
    this.pos_screen.addChild(this.pos_screen_comment);

    this.top_bar = new PIXI.Container();

    this.top_bar_text = new PIXI.Text(
        MONSTER.Common.trans("Language Monster", this.trans),
        this.sizes['36']
    );
    this.top_bar_loading_text = new PIXI.Text(
        MONSTER.Common.trans("Loading, please wait", this.trans), this.sizes['26']
    );

    this.loading_bar_pos_x = this.result_screen_x.left;
    this.loading_bar = new PIXI.Graphics();
    this.loading_bar.beginFill(this.colors.success, 0.8);
    this.loading_bar.drawRect(
        this.loading_bar_pos_x,
        this.game.height - 30,
        this.game.width,
        30
    );
    this.loading_bar.endFill();

    this.top_bar_text_pos = {
        'y': 0.5 * this.game.height - 0.5 * this.top_bar_text.height,
        'x': 0.5 * this.game.width - 0.5 * this.top_bar_text.width
    };

    this.top_bar_loading_text_pos = {
        'y': 0.7 * this.game.height - 0.5 * this.top_bar_loading_text.height,
        'x': 0.5 * this.game.width - 0.5 * this.top_bar_loading_text.width
    };

    this.top_bar_text.position.y = this.top_bar_text_pos.y;
    this.top_bar_text.position.x = this.top_bar_text_pos.x;
    this.top_bar_loading_text.position.y = this.top_bar_loading_text_pos.y;
    this.top_bar_loading_text.position.x = this.top_bar_loading_text_pos.x;

    this.top_bar.addChild(this.top_bar_text);
    this.top_bar.addChild(this.top_bar_loading_text);
    this.top_bar.addChild(this.loading_bar);

    this.init();

    var avail_games = window.games.concat(["ui"]);

    this.loader = MONSTER.Common.getLoader();

    console.log("Loading assets: " + avail_games);

    for (var i = 0; i < avail_games.length; i++) {
        var game_assets = game.assets[avail_games[i]];

        for (var img in game_assets) {
            if (game_assets.hasOwnProperty(img)) {
                console.log("Loading " + img + " " + game_assets[img]);

                this.loader.add(img, game_assets[img]);
            }
        }
    }
    this.loader.on('progress', function() {
        that.loading_bar_pos_x
            = Math.round(that.loader.progress / 100.0 * that.game.width);
    });
    this.loader.on('complete', function() {
        console.log("Assets loaded");

        that.kick_off();
    });

    // start loading: after loading the words, images will be loaded
    this.data_loader.loadWordPairs();

};

MONSTER.LoadingScreen.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.LoadingScreen.prototype.constructor = MONSTER.LoadingScreen;

MONSTER.LoadingScreen.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    this.loading_bar.position.x = this.loading_bar_pos_x;
};

MONSTER.LoadingScreen.prototype.start_loading = function() {
    this.game.word_sets = this.data_loader.word_sets;
    this.game.next_level();

    this.loader.load();
};

MONSTER.LoadingScreen.prototype.init = function()
{
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    this.game.view.addChild(this.top_bar);

};

MONSTER.LoadingScreen.prototype.kick_off = function() {
    this.game.kick_off();
};

MONSTER.SimpleGame = function(game)
{
    MONSTER.AbstractScreen.call(this, game);

    this.ID = 'simple';
    game.tutorial = 'modal-tut-simple';
    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------

    this.colors = {
        background: '0x243757',
        success: '0x33E46D',
        failure: '0xFF5039',

        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    // - end settings

    MONSTER.Common.setUpAjax();

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0,
        0,
        this.game.width,
        this.game.height
    );

    this.box = MONSTER.GoodWrongScreen(
        this.game,
        this.result_screen_x,
        this.result_screen_pos
    );

    this.init();
};

MONSTER.SimpleGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.SimpleGame.prototype.constructor = MONSTER.SimpleGame;

MONSTER.SimpleGame.prototype.onGamePause = function()
{
};

MONSTER.SimpleGame.prototype.onGamePauseOff = function()
{
};

MONSTER.SimpleGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);
};

MONSTER.SimpleGame.prototype.next_round = function() {
    var ctx = this;

    setTimeout(function() {
        ctx.init();
    }, 100);

    this.game.tweens.push(
        new MONSTER.Tween(
            this.box.box,
            'position.x',
            this.result_screen_x.left,
            1000
        )
    );
};

MONSTER.SimpleGame.prototype.resultScreen = function(is_correct)
{
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.SimpleGame.prototype.check_answer = function(answer)
{
    if (answer === this.answer)
        MONSTER.Common.correct(this);
    else
        MONSTER.Common.negative(this);
};

MONSTER.SimpleGame.prototype.init = function()
{
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    if ( ! MONSTER.Common.getWordSet(this))
    {
        return MONSTER.Common.endScreen(this);
    }

    var text = new PIXI.Text(
        this.question,
        {font: "36px Montserrat", fill: this.colors.question}
    );
    text.position.x = (this.game.width - text.width) / 2;
    text.position.y = 0.12 * this.game.height;
    this.game.view.addChild(text);

    var w = 250;
    var h = 90;
    var time = 1400;

    var b1 = MONSTER.Common.createButton(
        this,
        this.choices[0], 0, 0, w, h, -w, 150, function(){
            b1.interactive = false;
            context.check_answer(context.choices[0]);
        });
    b1.interactive = true;

    var b2 = MONSTER.Common.createButton(
        this,
        this.choices[1], 0, 0, w, h, this.game.width + w, 150, function(){
            b2.interactive = false;
            context.check_answer(context.choices[1]);
        });
    b2.interactive = true;

    var b3 = MONSTER.Common.createButton(
        this,
        this.choices[2], 0, 0, w, h, -w, 280, function(){
            b3.interactive = false;
            context.check_answer(context.choices[2]);
        });
    b3.interactive = true;

    var b4 = MONSTER.Common.createButton(
        this,
        this.choices[3], 0, 0, w, h, this.game.width + w, 280, function(){
            b4.interactive = false;
            context.check_answer(context.choices[3]);
        });
    b4.interactive = true;

    this.game.view.addChild(b1);
    this.game.view.addChild(b2);
    this.game.view.addChild(b3);
    this.game.view.addChild(b4);

    this.game.tweens.push(new MONSTER.Tween(b1, 'position.x', 75, time));
    this.game.tweens.push(new MONSTER.Tween(b2, 'position.x', 475, time));
    this.game.tweens.push(new MONSTER.Tween(b3, 'position.x', 75, time));
    this.game.tweens.push(new MONSTER.Tween(b4, 'position.x', 475, time));

    MONSTER.Common.addUI(this.game);
    this.box.box.position.x = this.result_screen_x.right;
    this.game.view.addChild(this.box.box);
    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);
};

MONSTER.SpaceGame = function(game)
{
    this.ID = 'space';
    game.tutorial = 'modal-tut-space';

    MONSTER.AbstractScreen.call(this, game);
    MONSTER.Key.blockScrolling();

    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------
    this.colors = {
        background: '0x7FBFFF',
        success: '0x33E46D',
        failure: '0xFF5039'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    // True during processing of a hit
    this.hit = false;

    // After hit ship is inactive for a while
    this.shipActive = true;

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["navy"]
    );

    this.rects = [
        new PIXI.Rectangle(70, 125, 200, 100),
        new PIXI.Rectangle(450, 125, 200, 100),
        new PIXI.Rectangle(70, 300, 200, 100),
        new PIXI.Rectangle(450, 300, 200, 100)
    ];

    this.answers = [];

    MONSTER.Common.setUpAjax();

    this.result_screen_on = false;

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0,
        0,
        this.game.width,
        this.game.height
    );

    this.box = MONSTER.GoodWrongScreen(
        this.game,
        this.result_screen_x,
        this.result_screen_pos
    );

    this.top_bar = new PIXI.Container();
    this.top_bar_text = new PIXI.Text("", this.sizes['36']);

    this.top_bar_y = {
        'show': 0.18 * this.game.height,
        'hide': - this.top_bar_text.height
    };

    this.top_bar_text.position.y = this.top_bar_y.hide;
    this.top_bar.addChild(this.top_bar_text);

    // List of assets

    this.urls = this.game.assets.space;

    this.time_to_reenable = 0;

    // Current speed
    this.ship_v = 0.0;

    // Max speed
    this.max_v = 4.8;

    // Min speed
    this.min_v = 0.8;

    this.drag = 0.0015;

    this.rotation_v = 0.0028;
    this.brakes = 0.001;

    this.acceleration = 0.003;

    this.assets = MONSTER.Utils.objectValues(this.urls);

    this.init();
};

MONSTER.SpaceGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.SpaceGame.prototype.constructor = MONSTER.SpaceGame;

MONSTER.SpaceGame.prototype.onGamePause = function()
{
};

MONSTER.SpaceGame.prototype.onGamePauseOff = function()
{
};

MONSTER.SpaceGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    if (! this.hit) {
        var delta = this.game.timeSinceLastFrame;
        this.moveShip();

        var new_x = this.island.position.x + delta * 0.0005 * -this.diff_x;
        var new_y = this.island.position.y + delta * 0.0005 * -this.diff_y;

        this.island.position.x = MONSTER.Utils.clamp(new_x, -25, 25);
        this.island.position.y = MONSTER.Utils.clamp(new_y, -25, 25);

        MONSTER.Common.parallax(
            delta,
            this.parallax,
            this.parallax_speed,
            800
        );

        if (this.shipActive)
            this.checkCollisions();
        else {
            this.time_to_reenable -= delta;

            if (this.time_to_reenable <= 0)
                this.enableShip();
        }
    }
};

MONSTER.SpaceGame.prototype.init = function()
{
    var FRAME_SZ = 78;
    var FRAMES = 6;

    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, '0x2d98a9');

    var ocean_t = PIXI.Texture.fromImage(this.urls.space_ocean);
    var clouds_t = PIXI.Texture.fromImage(this.urls.space_clouds);

    var ocean = [
        new PIXI.Sprite(ocean_t),
        new PIXI.Sprite(ocean_t)
    ];

    var clouds = [
        new PIXI.Sprite(clouds_t),
        new PIXI.Sprite(clouds_t)
    ];

    this.parallax = [
        clouds
    ];

    this.parallax_speed = [0.005, 0.02, 0.02, 0.04];

    this.game.background.addChild(ocean[0]);
    this.game.background.addChild(ocean[1]);

    ocean[1].position.x = 800;

    this.island = ocean[0];

    this.game.background.addChild(clouds[0]);
    this.game.background.addChild(clouds[1]);

    clouds[1].position.x = 800;

    var plane = PIXI.BaseTexture.fromImage(this.urls.space_plane);
    var plane_left = PIXI.BaseTexture.fromImage(this.urls.space_plane_left);
    var plane_right = PIXI.BaseTexture.fromImage(this.urls.space_plane_right);

    var textures = [];
    var textures_left = [];
    var textures_right = [];

    for (var i = 0; i < FRAMES; i++) {
        var rect = new PIXI.Rectangle(i * FRAME_SZ, 0, FRAME_SZ, FRAME_SZ);

        textures.push(new PIXI.Texture(plane, rect));
        textures_left.push(new PIXI.Texture(plane_left, rect));
        textures_right.push(new PIXI.Texture(plane_right, rect));
    }

    this.ship_normal = this.createShip(textures);
    this.ship_left = this.createShip(textures_left);
    this.ship_right = this.createShip(textures_right);

    this.game.view.addChild(this.ship_normal);
    this.game.view.addChild(this.ship_left);
    this.game.view.addChild(this.ship_right);

    // Initiate
    this.ship = this.ship_normal;
    this.ship.play();
    this.ship.position.x = this.game.width;
    this.ship.position.y = this.ship.height;
    this.ship_v = (this.max_v - this.min_v) / 2.0;
    this.ship.rotation = 3.0 / 2.0 * Math.PI;

    this.game.view.addChild(this.top_bar);

    this.box.box.position.x = this.result_screen_x.right;

    MONSTER.Common.addUI(this.game);
    this.game.view.addChild(this.box.box);
    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};

MONSTER.SpaceGame.prototype.createShip = function(textures) {
    var animation = new PIXI.extras.MovieClip(textures);

    animation.animationSpeed = 0.5;
    animation.anchor.x = animation.anchor.y = 0.5;
    animation.position.x = -1000;

    return animation;
};

MONSTER.SpaceGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.LEFT)) {
        this.ship.rotation -= t * this.rotation_v;

        this.turn(MONSTER.Const.LEFT);
    }
    else if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.RIGHT)) {
        this.ship.rotation += t * this.rotation_v;

        this.turn(MONSTER.Const.RIGHT);
    } else {
        this.turn(MONSTER.Const.AHEAD);
    }

    if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.UP))
        this.ship_v += t * this.acceleration + (1 / (this.max_v * this.max_v));
    else if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.DOWN))
        this.ship_v -= t * this.brakes;

    if (this.ship)
    {
        var x = this.ship.position.x;
        var y = this.ship.position.y;
        var angle = this.ship.rotation;
        // var new_x = x * Math.cos (angle) - y * Math.sin (angle);
        // var new_y = x * Math.sin (angle) + y * Math.cos (angle);

        this.ship.position.x += this.ship_v * Math.cos(angle - MONSTER.Const.PI_2);
        this.ship.position.y += this.ship_v * Math.sin(angle - MONSTER.Const.PI_2);

        this.diff_x = this.ship.position.x - x;
        this.diff_y = this.ship.position.y - y;
        // drag
        this.ship_v -= this.drag * t;

        if (this.ship_v < this.min_v)
            this.ship_v = this.min_v;
        if (this.ship_v > this.max_v)
            this.ship_v = this.max_v;

        if (this.ship.position.x > this.game.width)
            this.ship.position.x = this.game.width - this.ship.position.x;
        else if (this.ship.position.x < 0)
            this.ship.position.x = this.game.width - this.ship.position.x;
        if (this.ship.position.y > this.game.height)
            this.ship.position.y = this.game.height - this.ship.position.y;
        else if (this.ship.position.y < 0)
            this.ship.position.y = this.game.height - this.ship.position.y;
    }
};

MONSTER.SpaceGame.prototype.turn = function(direction) {
    var main = null;
    var other = [];

    if (direction === MONSTER.Const.LEFT) {
        main = this.ship_left;

        other.push(this.ship_normal);
        other.push(this.ship_right);
    } else if (direction === MONSTER.Const.RIGHT) {
        main = this.ship_right;

        other.push(this.ship_normal);
        other.push(this.ship_left);
    } else {
        main = this.ship_normal;

        other.push(this.ship_right);
        other.push(this.ship_left);
    }

    main.position.x = this.ship.position.x;
    main.position.y = this.ship.position.y;
    main.rotation = this.ship.rotation;

    main.play();

    for (var i = 0; i < 2; i++) {
        other[i].stop();
        other[i].position.x = -1000;
    }

    this.ship = main;
};

MONSTER.SpaceGame.prototype.checkCollisions = function()
{
    if (this.ship && this.ship_v > 0 && ! this.hit)
    {
        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];

            if (obj.r.contains(this.ship.position.x, this.ship.position.y))
            {
                this.hit = true;
                this.shipActive = false;

                this.ship_normal.alpha
                    = this.ship_left.alpha
                    = this.ship_right.alpha = 0.5;

                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
        }
    }
};

MONSTER.SpaceGame.prototype.enableShip = function()
{
    this.shipActive = true;

    this.ship_normal.alpha
        = this.ship_left.alpha
        = this.ship_right.alpha = 1.0;
};

MONSTER.SpaceGame.prototype.disableShip = function()
{
    this.shipActive = false;

    this.ship_normal.alpha
        = this.ship_left.alpha
        = this.ship_right.alpha = 0.5;
};


MONSTER.SpaceGame.prototype.moveOutOfScreen = function()
{
    // question

    this.game.tweens.push(new MONSTER.Tween(
        this.top_bar, 'position.y', this.top_bar_y.hide, 1000));

    // answers

    for (var i = 0; i < this.answers.length; i++)
    {
        var obj = this.answers[i];

        if (obj.text.position.x < this.game.width / 2.0)
            this.game.tweens.push(new MONSTER.Tween(
                obj.text, 'position.x', - obj.text.width / 2, 1000));
        else
            this.game.tweens.push(new MONSTER.Tween(
                obj.text,
                'position.x',
                this.game.width + obj.text.width / 2,
                1000
            ));
    }
};

MONSTER.SpaceGame.prototype.resultScreen = function(is_correct)
{
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.SpaceGame.prototype.next_round = function()
{
    this.answers.length = 0;
    this.game.tweens.length = 0;

    if ( ! MONSTER.Common.getWordSet(this)) {
        return MONSTER.Common.endScreen(this);
    }

    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x = (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit) {
        // not the first round

        this.game.tweens.push(
            new MONSTER.Tween(
                this.box.box, 'position.x', this.result_screen_x.left, 1000
            )
        );
        this.time_to_reenable = 1500;
    }

    this.game.tweens.push(
        new MONSTER.Tween(
            this.top_bar, 'position.y', this.top_bar_y.show, 1000
        )
    );

    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.SpaceGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];

    var rx = Math.floor(Math.random() * r.width + r.x);
    var ry = Math.floor(Math.random() * r.height + r.y);

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);

    MONSTER.Common.secure_answer_size(text, sizes, 150);

    var add = function()
    {
        if (rx < context.game.width / 2.0)
            text.position.x = -text.width;
        else
            text.position.x = context.game.width + text.width;

        text.position.y = ry;
        text.anchor.x = text.anchor.y = 0.5;
        context.game.background.addChild(text);

        var rect_ = new PIXI.Rectangle(
            rx - text.width / 2,
            text.position.y - text.height / 2,
            text.width,
            text.height
        );
        var item_ = {
            'r' : rect_,
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);

        context.game.tweens.push(new MONSTER.Tween(text, 'position.x', rx, 1000));
    };

    add();
};

MONSTER.PlaneGame = function(game)
{
    this.ID = 'plane';
    game.tutorial = 'modal-tut-plane';

    MONSTER.AbstractScreen.call(this, game);
    MONSTER.Key.blockScrolling();

    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------
    this.colors = {
        background: '0x76D3DE',

        success: '0x33E46D',
        failure: '0xFF5039'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    // True durign processing of a hit
    this.hit = false;

    this.constant_answer_speed = false;

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["navy"]
    );

    this.rects = [
        new PIXI.Rectangle(70, 125, 200, 100),
        new PIXI.Rectangle(450, 125, 200, 100),
        new PIXI.Rectangle(70, 300, 200, 100),
        new PIXI.Rectangle(450, 300, 200, 100)
    ];

    this.answers = [];

    MONSTER.Common.setUpAjax();

    this.result_screen_on = false;

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0,
        0,
        this.game.width,
        this.game.height
    );

    this.box = MONSTER.GoodWrongScreen(
        this.game,
        this.result_screen_x,
        this.result_screen_pos
    );

    this.top_bar = new PIXI.Container();
    this.top_bar_text = new PIXI.Text("", this.sizes['36']);

    this.top_bar_y = {
        'show': 0.18 * this.game.height,
        'hide': - this.top_bar_text.height
    };

    this.top_bar_text.position.y = this.top_bar_y.hide;
    this.top_bar.addChild(this.top_bar_text);

    // List of assets

    this.urls = this.game.assets.plane;

    // Current speed
    this.ship_v = 0.0;

    // Max speed
    this.max_v = 6.0;

    this.drag = 0.0015;

    this.rotation_v = 0.0028;
    this.brakes = 0.001;

    this.acceleration = 0.003;

    this.assets = MONSTER.Utils.objectValues(this.urls);

    this.init();
};

MONSTER.PlaneGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.PlaneGame.prototype.constructor = MONSTER.PlaneGame;

MONSTER.PlaneGame.prototype.onGamePause = function()
{
};

MONSTER.PlaneGame.prototype.onGamePauseOff = function()
{
};

MONSTER.PlaneGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    if ( ! this.hit) {
        var delta = this.game.timeSinceLastFrame;

        this.moveShip();

        MONSTER.Common.parallax(delta, this.parallax, this.parallax_speed, 800);

        if (this.answers && this.game.actual_rounds) {
            for (var i = 0; i < this.answers.length; i++) {
                if (this.constant_answer_speed) {
                    this.answers[i].text.position.x -= delta * 0.14;
                } else {
                    this.answers[i].text.position.x -=
                        MONSTER.linear(
                            this.game.round_id,
                            0,
                            this.game.actual_rounds - 1,
                            0.08,
                            0.1
                        ) * delta;
                }
            }
        }

        this.checkCollisions();
    }
};

MONSTER.PlaneGame.prototype.init = function()
{
    this.game.background.clear();
    this.game.view.removeChildren();

    var sky_t = PIXI.Texture.fromImage(this.urls.plane_sky);
    var background_t = PIXI.Texture.fromImage(this.urls.plane_background);
    var valley_t = PIXI.Texture.fromImage(this.urls.plane_valley);
    var hills_t = PIXI.Texture.fromImage(this.urls.plane_hills);

    var sky = [new PIXI.Sprite(sky_t)];
    var background = [
        new PIXI.Sprite(background_t),
        new PIXI.Sprite(background_t)
    ];

    var valley = [
        new PIXI.Sprite(valley_t),
        new PIXI.Sprite(valley_t)
    ];

    var hills = [
        new PIXI.Sprite(hills_t),
        new PIXI.Sprite(hills_t)
    ];

    this.parallax = [
        background,
        valley,
        hills
    ];

    this.parallax_speed = [0.01, 0.03, 0.05];

    this.game.background.addChild(sky[0]);

    this.game.background.addChild(background[0]);
    this.game.background.addChild(background[1]);
    this.game.background.addChild(valley[0]);
    this.game.background.addChild(valley[1]);
    this.game.background.addChild(hills[0]);
    this.game.background.addChild(hills[1]);

    background[1].position.x = 800;
    background[0].position.y = 450 - 260;
    background[1].position.y = 450 - 260;

    valley[1].position.x = 800;
    valley[0].position.y = 450 - 180;
    valley[1].position.y = 450 - 180;

    hills[1].position.x = 800;
    hills[0].position.y = 450 - 251;
    hills[1].position.y = 450 - 251;

    // -- end init parallax

    var textures = [];

    var plane = PIXI.BaseTexture.fromImage(this.urls.plane_plane);

    var FRAMES = 5;
    var FRAME_W = 100;
    var FRAME_H = 60;

    for (var i = 0; i < FRAMES; i++) {
        var rect_run = new PIXI.Rectangle(i * FRAME_W, 0, FRAME_W, FRAME_H);

        textures.push(new PIXI.Texture(plane, rect_run));
    }

    this.ship = new PIXI.extras.MovieClip(textures);
    this.ship.animationSpeed = 0.5;
    this.ship.play();

    this.game.view.addChild(this.ship);

    this.ship.anchor.x = 0.5;
    this.ship.anchor.y = 0.5;

    var start_y = 0.25 * this.game.height;
    var stop_y = 0.83 * this.game.height;

    this.ship.position.x = 0.2 * this.game.width;
    this.ship.position.y = start_y;

    this.ship.start_y = start_y;
    this.ship.stop_y = stop_y;
    this.ship.v_time = 0;

    // movement UP
    this.ship.v_up = false;
    this.ship.v_up_tmp = 0;

    this.game.view.addChild(this.top_bar);

    this.box.box.position.x = this.result_screen_x.right;

    MONSTER.Common.addUI(this.game);
    this.game.view.addChild(this.box.box);
    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};

MONSTER.PlaneGame.prototype.moveShip = function()
{
    var delta = this.game.timeSinceLastFrame;

    var rotation = 0;
    var v_up = false;

    if (MONSTER.Key.isDown(MONSTER.Key.UP)) {
        v_up = true;
        rotation = MONSTER.Utils.to_radians(-10);
    }

    var top_edge = Math.round(0.14 * this.game.height);

    if (this.ship.position.y <= top_edge) {
        // Ship is near the top edge - we will keep it there as long
        // the user wants it to fly upwards

        if (v_up) {
            this.ship.position.y = top_edge;
            this.ship.rotation = 0;

            return;
        }
    }

    this.ship.rotation = rotation;
    this.ship.v_up = v_up;

    if (this.ship) {
        if (this.ship.v_up) {
            // Flying upwards

            this.ship.start_y = this.ship.position.y;
            this.ship.v_time = 0.0;

            var y_movement = delta * 0.11; // Speed of going up
            this.ship.position.y -= y_movement;
        } else {
            // Falling down

            var T = 2000.0;

            this.ship.v_time += delta;
            this.ship.rotation = 0;

            var pct = MONSTER.Easing.easeInOutQuart(this.ship.v_time / T);

            this.ship.position.y = Math.round(
                pct * (this.ship.stop_y - this.ship.start_y)
            ) + this.ship.start_y;

            if (this.ship.v_time > T)
                this.ship.position.y = this.ship.stop_y;
        }
    }
};

MONSTER.PlaneGame.prototype.checkCollisions = function()
{
    if (this.ship && ! this.hit) {
        var left = 0;

        for (var i = 0; i < this.answers.length; i++) {
            var obj = this.answers[i];

            if (Math.abs(obj.text.position.x - this.ship.position.x)
                < this.ship.width / 2
                && Math.abs(obj.text.position.y - this.ship.position.y)
                < this.ship.height / 2
            ) {
                this.hit = true;
                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
            else if (obj.text.position.x < obj.text.width / 2)
            {
                left++;
            }
        }

        if (left == this.answers.length)
        {
            this.constant_answer_speed = true;
            this.hit = true;
            this.moveOutOfScreen();
            MONSTER.Common.negative(this);
        }
    }
};


MONSTER.PlaneGame.prototype.moveOutOfScreen = function()
{
    // question

    this.game.tweens.push(new MONSTER.Tween(
        this.top_bar, 'position.y', this.top_bar_y.hide, 1000));

    // answers

    for (var i = 0; i < this.answers.length; i++) {
        var obj = this.answers[i];

        if (obj.text.position.x < this.game.width / 2.0)
            this.game.tweens.push(new MONSTER.Tween(
                obj.text, 'position.x', - obj.text.width / 2, 1000));
        else
            this.game.tweens.push(new MONSTER.Tween(
                obj.text,
                'position.x', this.game.width + obj.text.width / 2, 1000));
    }
};

MONSTER.PlaneGame.prototype.resultScreen = function(is_correct)
{
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.PlaneGame.prototype.next_round = function()
{
    this.answers.length = 0;
    this.game.tweens.length = 0;

    if ( ! MONSTER.Common.getWordSet(this)) {
        return MONSTER.Common.endScreen(this);
    }

    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x =
        (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit) {
        // not the first round

        this.game.tweens.push(new MONSTER.Tween(
            this.box.box, 'position.x', this.result_screen_x.left, 1000));
    }

    this.game.tweens.push(new MONSTER.Tween(
        this.top_bar, 'position.y', this.top_bar_y.show, 1000));
    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.PlaneGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);

    MONSTER.Common.secure_answer_size(text, sizes, 150);

    var add = function()
    {
        text.position.x = 0.7 * Math.floor(Math.random() * r.width + r.x)
            + 0.7 * this.game.width;
        text.position.y = Math.floor(Math.random() * r.height + r.y);

        text.anchor.x = text.anchor.y = 0.5;
        context.game.background.addChild(text);

        var item_ = {
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);
    };

    add();
};

MONSTER.RunnerGame = function(game)
{
    this.ID = 'runner';
    game.tutorial = 'modal-tut-runner';

    MONSTER.AbstractScreen.call(this, game);
    MONSTER.Key.blockScrolling();

    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------
    this.colors = {
        background: '0x76D3DE',

        success: '0x33E46D',
        failure: '0xFF5039'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    // True durign processing of a hit
    this.hit = false;

    // After hit ship is inactive for a while
    this.shipActive = true;

    this.constant_answer_speed = false;

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["white"]
    );

    this.rects = [
        new PIXI.Rectangle(0, 240, 100, 100),
        new PIXI.Rectangle(500, 240, 100, 100),
        new PIXI.Rectangle(1000, 240, 100, 100),
        new PIXI.Rectangle(1500, 240, 100, 100)
    ];

    this.answers = [];

    MONSTER.Common.setUpAjax();

    this.result_screen_on = false;

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0,
        0,
        this.game.width,
        this.game.height
    );

    this.box = MONSTER.GoodWrongScreen(
        this.game,
        this.result_screen_x,
        this.result_screen_pos
    );

    this.top_bar = new PIXI.Container();
    this.top_bar_text = new PIXI.Text("", this.sizes['36']);

    this.top_bar_y = {
        'show': 0.18 * this.game.height,
        'hide': - this.top_bar_text.height
    };

    this.top_bar_text.position.y = this.top_bar_y.hide;
    this.top_bar.addChild(this.top_bar_text);

    // List of assets

    this.urls = this.game.assets.runner;

    // Current speed
    this.ship_v = 0.0;

    // Max speed
    this.max_v = 6.0;

    this.drag = 0.0015;

    this.rotation_v = 0.0028;
    this.brakes = 0.001;

    this.acceleration = 0.003;

    this.State = {
        'RUNNING': 0,
        'JUMPING': 1,
        'FALLING': 2,
        'SLIDING': 3
    };

    this.state = this.State.RUNNING;
    this.JUMP_TIME = 600.0;

    this.assets = MONSTER.Utils.objectValues(this.urls);

    this.init();
};

MONSTER.RunnerGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.RunnerGame.prototype.constructor = MONSTER.RunnerGame;

MONSTER.RunnerGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    var delta = this.game.timeSinceLastFrame;

    if (! this.hit) {
        MONSTER.Common.parallax(delta, this.parallax, this.parallax_speed, 800);
        this.moveShip();

        if (this.answers && this.game.actual_rounds) {
            for (var i = 0; i < this.answers.length; i++) {
                this.answers[i].text.position.x -=
                    MONSTER.linear(
                        this.game.round_id,
                        0,
                        this.game.actual_rounds - 1,
                        0.2,
                        0.23
                    ) * delta;
            }
        }

        if (this.shipActive)
            this.checkCollisions();
    }
};

MONSTER.RunnerGame.prototype.onGamePause = function()
{
    this.ship.gotoAndStop(1);
};

MONSTER.RunnerGame.prototype.onGamePauseOff = function()
{
    this.ship.play();
};

MONSTER.RunnerGame.prototype.init = function()
{
    this.game.background.clear();
    this.game.view.removeChildren();

    var far_background = PIXI.Texture.fromImage(this.urls.runner_far_background);
    var background = PIXI.Texture.fromImage(this.urls.runner_background);
    var tree = PIXI.Texture.fromImage(this.urls.runner_trees);
    var foreground = PIXI.Texture.fromImage(this.urls.runner_foreground);
    var ground = PIXI.Texture.fromImage(this.urls.runner_ground);

    var far_backgrounds = [
        new PIXI.Sprite(far_background),
        new PIXI.Sprite(far_background)
    ];

    var backgrounds = [
        new PIXI.Sprite(background),
        new PIXI.Sprite(background)
    ];

    var trees = [
        new PIXI.Sprite(tree),
        new PIXI.Sprite(tree)
    ];

    var foregrounds = [
        new PIXI.Sprite(foreground),
        new PIXI.Sprite(foreground)
    ];

    var grounds = [
        new PIXI.Sprite(ground),
        new PIXI.Sprite(ground)
    ];

    this.parallax = [
        far_backgrounds,
        backgrounds,
        trees,
        grounds,
        foregrounds
    ];

    this.parallax_speed = [0.01, 0.03, 0.05, 0.07, 0.1];

    far_backgrounds[0].position.x = 0;
    far_backgrounds[1].position.x = 800;
    backgrounds[0].position.x = 0;
    backgrounds[1].position.x = 800;
    trees[0].position.x = 0;
    trees[1].position.x = 800;

    grounds[0].position.x = 0;
    grounds[0].position.y = 450 - 64;
    grounds[1].position.x = 800;
    grounds[1].position.y = 450 - 64;

    foregrounds[0].position.x = 0;
    foregrounds[0].position.y = 450 - 195;
    foregrounds[1].position.x = 800;
    foregrounds[1].position.y = 450 - 195;

    this.game.background.addChild(far_backgrounds[0]);
    this.game.background.addChild(far_backgrounds[1]);
    this.game.background.addChild(backgrounds[0]);
    this.game.background.addChild(backgrounds[1]);
    this.game.background.addChild(trees[0]);
    this.game.background.addChild(trees[1]);

    this.textures = [];
    this.textures_jump = [];

    var FRAME_W = 88;
    var FRAME_RUN_H = 150;
    var FRAME_JUMP_H = 158;
    var FRAMES_RUN = 8;

    var panda_run = PIXI.BaseTexture.fromImage(this.urls.runner_run);
    var panda_jump = PIXI.BaseTexture.fromImage(this.urls.runner_jump);

    for (var i = 0; i < FRAMES_RUN; i++) {
        var rect_run = new PIXI.Rectangle(i * FRAME_W, 0, FRAME_W, FRAME_RUN_H);
        this.textures.push(new PIXI.Texture(panda_run, rect_run));

        if (i > 0) {
            // Animation with 0th frame does not look good
            var rect_jump = new PIXI.Rectangle(i * FRAME_W, 0, FRAME_W, FRAME_JUMP_H);
            this.textures_jump.push(new PIXI.Texture(panda_jump, rect_jump));
        }
    }

    this.ship = new PIXI.extras.MovieClip(this.textures);
    this.ship.animationSpeed = 0.2;
    this.ship.play();

    this.ship.anchor.x = 0.5;
    this.ship.anchor.y = 0.5;

    var stop_y = 0.56 * this.game.height;
    var start_y = 0.71 * this.game.height;

    this.original_y = 0.71 * this.game.height;
    this.slide_y = 0.82 * this.game.height;

    this.ship.position.x = 0.2 * this.game.width;
    this.ship.position.y = start_y;

    this.ship.start_y = start_y;
    this.ship.stop_y = stop_y;
    this.ship.v_time = 0;

    // movement UP
    this.ship.v_up = false;
    this.ship.v_down = false;

    this.game.view.addChild(this.top_bar);

    this.box.box.position.x = this.result_screen_x.right;

    this.game.view.addChild(grounds[0]);
    this.game.view.addChild(grounds[1]);

    this.game.view.addChild(this.ship);

    this.game.view.addChild(foregrounds[0]);
    this.game.view.addChild(foregrounds[1]);

    MONSTER.Common.addUI(this.game);
    this.game.view.addChild(this.box.box);

    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};

MONSTER.RunnerGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (this.state === this.State.RUNNING) {
        if (MONSTER.Key.isUp(MONSTER.Key.UP)) {
            this.state = this.State.JUMPING;
            this.ship.textures = this.textures_jump;
            this.ship.start_y = this.ship.position.y;
            this.ship.stop_y = this.ship.start_y - 200;
        }
    }

    if (this.state === this.State.RUNNING) {
        if (MONSTER.Key.isDown(MONSTER.Key.DOWN)) {
            this.state = this.State.SLIDING;
            this.ship.rotation = 0.75 * 2.0 * MONSTER.Const.PI;
            this.ship.gotoAndStop(1);
            this.ship.position.y = this.slide_y;
        }
    }

    if (this.state === this.State.SLIDING) {
        if (!MONSTER.Key.isDown(MONSTER.Key.DOWN)) {
            // Stand up after sliding

            this.state = this.State.RUNNING;
            this.ship.rotation = 0;
            this.ship.play();
            this.ship.position.y = this.original_y;
        }
    } else if (this.state === this.State.JUMPING) {
        this.ship.v_time += t;

        var pct = MONSTER.Easing.easeOutQuart(this.ship.v_time / this.JUMP_TIME);

        // Move upwards
        this.ship.position.y = Math.round(
            pct * (this.ship.stop_y - this.ship.start_y))
            + this.ship.start_y;

        if (this.ship.v_time > this.JUMP_TIME) {
            // Falling now

            this.ship.v_time = 0.0;
            this.state = this.State.FALLING;
            this.ship.position.y = this.ship.stop_y;
        }
    }

    if (this.state === this.State.FALLING
        && this.ship.position.y < this.original_y) {
        // Move downwards

        this.ship.position.y += t * 0.3;
    }

    if (this.state === this.State.FALLING
        && this.ship.position.y >= this.original_y) {
        // Back on the ground

        this.state = this.State.RUNNING;
        this.ship.textures = this.textures;
    }
};

MONSTER.RunnerGame.prototype.checkCollisions = function()
{
    if (this.ship && ! this.hit)
    {
        var left = 0;

        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];
            var collision = false;

            if (this.ship.v_down)
            {
                if (obj.text.position.x >= this.ship.position.x - this.ship.width / 2 &&
                    obj.text.position.x <= this.ship.position.x + this.ship.width / 2 &&
                    obj.text.position.y >= this.ship.position.y - this.ship.height / 2.5 &&
                    obj.text.position.y <= this.ship.position.y + this.ship.height / 2.5
                )
                    collision = true;
            }
            else
            {
                if (obj.text.position.x >= this.ship.position.x - this.ship.width / 2 &&
                    obj.text.position.x <= this.ship.position.x + this.ship.width / 2 &&
                    obj.text.position.y >= this.ship.position.y - this.ship.height / 2 &&
                    obj.text.position.y <= this.ship.position.y + this.ship.height / 2
                )
                    collision = true;
            }

            if (collision)
            {
                this.hit = true;
                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
            else if (obj.text.position.x < obj.text.width / 2)
            {
                left++;
            }
        }

        if (left === this.answers.length && this.state === this.State.RUNNING)
        {
            this.constant_answer_speed = true;
            this.hit = true;
            this.moveOutOfScreen();
            MONSTER.Common.negative(this);
        }
    }
};


MONSTER.RunnerGame.prototype.moveOutOfScreen = function()
{
    // question

    this.game.tweens.push(new MONSTER.Tween(
        this.top_bar, 'position.y', this.top_bar_y.hide, 1000));

    // answers

    for (var i = 0; i < this.answers.length; i++)
    {
        var obj = this.answers[i];

        if (obj.text.position.x < this.game.width / 2.0)
            this.game.tweens.push(new MONSTER.Tween(
                obj.text, 'position.x', - obj.text.width / 2, 1000));
        else
            this.game.tweens.push(new MONSTER.Tween(
                obj.text,
                'position.x',
                this.game.width + obj.text.width / 2,
                1000
            ));
    }
};

MONSTER.RunnerGame.prototype.resultScreen = function(is_correct) {
    this.ship.stop();
    // result_screen_on = true;

    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.RunnerGame.prototype.next_round = function()
{
    this.answers.length = 0;
    this.game.tweens.length = 0;

    if ( ! MONSTER.Common.getWordSet(this)) {
        return MONSTER.Common.endScreen(this);
    }

    this.ship.play();
    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x = (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit)
    {
        // not the first round
        this.game.tweens.push(new MONSTER.Tween(
            this.box.box, 'position.x', this.result_screen_x.left, 1000));

        this.game.setStopFunc(this.activateShipAgain, 1500, this);
    }

    this.game.tweens.push(
        new MONSTER.Tween(
            this.top_bar,
            'position.y',
            this.top_bar_y.show,
            1000
        )
    );

    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.RunnerGame.prototype.activateShipAgain = function()
{
    this.shipActive = true;
};

MONSTER.RunnerGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);
    text.style = sizes[sizeId];

    var max_size = 150;
    MONSTER.Common.secure_answer_size(text, sizes, max_size);

    var add = function()
    {
        text.position.x = 1 * Math.floor(Math.random() * r.width + r.x) + 1 * this.game.width;
        text.position.y = Math.floor(Math.random() * r.height + r.y);

        text.anchor.x = text.anchor.y = 0.5;
        context.game.background.addChild(text);

        var item_ = {
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);
    };

    add();
};

MONSTER.ShooterGame = function(game)
{
    this.ID = 'shooter';
    game.tutorial = 'modal-tut-shooter';

    MONSTER.AbstractScreen.call(this, game);
    MONSTER.Key.blockScrolling();

    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------
    this.colors = {
        background: '0x76D3DE',

        success: '0x33E46D',
        failure: '0xFF5039'
    };

    this.button_colors = {
        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
    };

    // Milliseconds to reach the target
    this.SNOWBALL_TIME = 700.0;

    // True durign processing of a hit
    this.hit = false;

    // After hit ship is inactive for a while
    this.shipActive = true;

    this.constant_answer_speed = false;

    this.sizes = MONSTER.getFonts(
        MONSTER.Const.DEFAULT_FONT_FAMILY,
        MONSTER.Const.COLOURS["navy"]
    );

    this.rects = [
        new PIXI.Rectangle(0, 130, 100, 90),
        new PIXI.Rectangle(300, 130, 100, 90),
        new PIXI.Rectangle(600, 130, 100, 90),
        new PIXI.Rectangle(900, 130, 100, 90)
    ];

    this.answers = [];

    MONSTER.Common.setUpAjax();

    this.result_screen_on = false;

    this.result_screen_x = {
        'show' : 0,
        'right' : this.game.width,
        'left' : - this.game.width
    };

    this.result_screen_pos = new PIXI.Rectangle(
        0,
        0,
        this.game.width,
        this.game.height
    );

    this.box = MONSTER.GoodWrongScreen(
        this.game,
        this.result_screen_x,
        this.result_screen_pos
    );

    this.top_bar = new PIXI.Container();
    this.top_bar_text = new PIXI.Text("", this.sizes['36']);

    this.top_bar_y = {
        'show': 0.18 * this.game.height,
        'hide': - this.top_bar_text.height
    };

    this.top_bar_text.position.y = this.top_bar_y.hide;
    this.top_bar.addChild(this.top_bar_text);

    // List of assets

    this.urls = this.game.assets.shooter;

    // Current speed
    this.ship_v = 0.0;

    // Max speed
    this.max_v = 6.0;

    this.drag = 0.0015;

    this.rotation_v = 0.0028;
    this.brakes = 0.001;

    this.acceleration = 0.003;

    this.assets = MONSTER.Utils.objectValues(this.urls);

    this.init();
};

MONSTER.ShooterGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.ShooterGame.prototype.constructor = MONSTER.ShooterGame;

MONSTER.ShooterGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    if ( ! this.hit) {
        this.move();

        var delta = this.game.timeSinceLastFrame;

        MONSTER.Common.parallax(delta, this.parallax, this.parallax_speed, 800);

        if (this.answers && this.game.actual_rounds) {
            var left = 0;

            for (var i = 0; i < this.answers.length; i++) {
                if (this.constant_answer_speed) {
                    this.answers[i].text.position.x -= delta * 0.16;
                } else {
                    this.answers[i].text.position.x -=
                        MONSTER.linear(
                            this.game.round_id,
                            0,
                            this.game.actual_rounds - 1,
                            0.16,
                            0.19
                        ) * delta;
                }

                if (this.answers[i].text.position.x
                    + this.answers[i].text.width < 0) {
                    left++;
                }
            }

            if (left == this.answers.length) {
                this.constant_answer_speed = true;
                this.hit = true;
                this.removeAnswers(this.answers);
                MONSTER.Common.negative(this);
            }
        }
    }
};

MONSTER.ShooterGame.prototype.onGamePause = function()
{
};

MONSTER.ShooterGame.prototype.onGamePauseOff = function()
{
    MONSTER.Common.hideCursor();
};

MONSTER.ShooterGame.prototype.mousemove = function(mouseData)
{
    this.crosshair.position.x = mouseData.data.global.x;
    this.crosshair.position.y = mouseData.data.global.y;
};

MONSTER.ShooterGame.prototype.init = function()
{
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.hideCursor();

    var background_t = PIXI.Texture.fromImage(this.urls.shooter_background);
    var clouds_t = PIXI.Texture.fromImage(this.urls.shooter_clouds);
    var middle_t = PIXI.Texture.fromImage(this.urls.shooter_middle);
    var foreground_t = PIXI.Texture.fromImage(this.urls.shooter_foreground);

    var background = [
        new PIXI.Sprite(background_t),
        new PIXI.Sprite(background_t)
    ];

    var clouds = [
        new PIXI.Sprite(clouds_t),
        new PIXI.Sprite(clouds_t)
    ];

    var middle = [
        new PIXI.Sprite(middle_t),
        new PIXI.Sprite(middle_t)
    ];

    var foreground = [
        new PIXI.Sprite(foreground_t),
        new PIXI.Sprite(foreground_t)
    ];

    this.parallax = [
        clouds,
        background,
        middle,
        foreground
    ];

    this.parallax_speed = [0.01, 0.02, 0.02, 0.04];

    this.game.background.addChild(background[0]);
    this.game.background.addChild(background[1]);
    this.game.background.addChild(clouds[0]);
    this.game.background.addChild(clouds[1]);
    this.game.background.addChild(middle[0]);
    this.game.background.addChild(middle[1]);
    this.game.background.addChild(foreground[0]);
    this.game.background.addChild(foreground[1]);

    background[0].position.y = 450 - 484;
    background[1].position.y = 450 - 484;
    background[1].position.x = 800;

    clouds[1].position.x = 800;

    middle[1].position.x = 800;
    middle[0].position.y = 450 - 230;
    middle[1].position.y = 450 - 230;

    foreground[1].position.x = 800;
    foreground[0].position.y = 450 - 320;
    foreground[1].position.y = 450 - 320;

    this.crosshair_t = PIXI.Texture.fromImage(this.urls.shooter_crosshair);

    var snowball_t = PIXI.Texture.fromImage(this.urls.shooter_snowball);

    this.snowball = {
        'sprite': new PIXI.Sprite(snowball_t),
        'src': [0, 0],
        'dest': [0, 0],
        'time': 0,
        'thrown': false,

        // Current
        'pos': [0, 0]
    };

    this.crosshair = new PIXI.Sprite(this.crosshair_t);
    this.crosshair.anchor.x = this.crosshair.anchor.y = 0.5;
    this.crosshair.position.x = this.game.width * 0.5;
    this.crosshair.position.y = this.game.height * 0.5;

    this.game.view.interactive = true;
    this.game.view.on('mousemove', this.mousemove.bind(this));
    this.game.view.on('click', this.throw.bind(this));

    this.game.view.addChild(this.top_bar);

    this.box.box.position.x = this.result_screen_x.right;

    this.game.view.addChild(this.crosshair);
    this.game.view.addChild(this.snowball.sprite);

    this.resetSnowball(this.snowball);

    MONSTER.Common.addUI(this.game);

    this.game.view.addChild(this.box.box);

    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};

MONSTER.ShooterGame.prototype.move = function()
{
    if (this.snowball.thrown) {
        var snowball = this.snowball;
        var delta = this.game.timeSinceLastFrame;

        var sprite = snowball.sprite;

        sprite.position.x = snowball.pos[0];
        sprite.position.y = snowball.pos[1];

        snowball.time += delta;

        if (snowball.time < this.SNOWBALL_TIME) {
            var new_pos = MONSTER.Utils.bezier(
                snowball.time / this.SNOWBALL_TIME, [
                    {
                        'x': snowball.src[0],
                        'y': snowball.src[1]
                    },
                    {
                        'x': (snowball.src[0] + snowball.dest[0]) / 2.0,
                        'y': (snowball.src[1] + snowball.dest[1]) / 2.0
                    },
                    {
                        'x': snowball.dest[0],
                        'y': snowball.dest[1]
                    }
                ]
            );

            sprite.position.x = new_pos.x;
            sprite.position.y = new_pos.y;

            var scale = this.SNOWBALL_TIME / 2.0 / snowball.time;

            sprite.visible = scale < 4;
            sprite.scale.x = sprite.scale.y = scale;

            this.checkHit(sprite.position.x, sprite.position.y);
        } else
            this.resetSnowball(this.snowball);
    }
};

MONSTER.ShooterGame.prototype.resetSnowball = function(snowball)
{
    snowball.sprite.anchor.x = snowball.sprite.anchor.y = 0.5;
    snowball.src = [0, 0];
    snowball.pos = [0, 0];
    snowball.time = 0;
    snowball.thrown = false;
};

MONSTER.ShooterGame.prototype.throw = function()
{
    var snowball = this.snowball;

    if (! snowball.thrown) {
        snowball.thrown = true;

        var pos_x = MONSTER.linear(
            this.crosshair.position.x,
            0,
            this.game.width,
            this.game.width * 0.2, this.game.width * 0.8
        );

        var pos_y = this.game.height + snowball.sprite.height;

        snowball.src = [pos_x, pos_y];
        snowball.pos = [pos_x, pos_y];
        snowball.dest = [this.crosshair.position.x, this.crosshair.position.y];
    }
};

MONSTER.ShooterGame.prototype.checkHit = function(x, y)
{
    if (! this.hit) {
        for (var i = 0; i < this.answers.length; i++) {
            var obj = this.answers[i];

            if (MONSTER.Utils.isPointInRectWithTol(x, y, [
                obj.text.position.x,
                obj.text.position.y,
                obj.text.width,
                obj.text.height
            ], [20, 40])) {
                this.game.tweens.push(
                    new MONSTER.Tween(
                        obj.text,
                        'position.y',
                        -200,
                        1000
                    )
                );
                this.game.tweens.push(
                    new MONSTER.Tween(
                        obj.text,
                        'position.x',
                        MONSTER.Utils.getRandomInt(
                            0.2 * this.game.width,
                            0.8 * this.game.width
                        ),
                        1000
                    )
                );

                var answers = MONSTER.Common.getAnswersMinusCurrent(
                    this.answers, obj
                );

                this.hit = true;
                this.removeAnswers(answers);

                if (obj.word === this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);

            }
        }
    }
};


MONSTER.ShooterGame.prototype.removeAnswers = function(answers)
{
    // question

    this.game.tweens.push(new MONSTER.Tween(
        this.top_bar, 'position.y', this.top_bar_y.hide, 1000));

    // answers

    for (var i = 0; i < answers.length; i++) {
        var obj = answers[i];

        if (obj.text.position.x < this.game.width / 2.0)
            this.game.tweens.push(new MONSTER.Tween(
                obj.text, 'position.x', - obj.text.width / 2, 1000));
        else
            this.game.tweens.push(new MONSTER.Tween(
                obj.text,
                'position.x',
                this.game.width + obj.text.width / 2,
                1000
            ));
    }
};

MONSTER.ShooterGame.prototype.resultScreen = function(is_correct)
{
    // result_screen_on = true;
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.ShooterGame.prototype.next_round = function()
{
    this.answers.length = 0;
    this.game.tweens.length = 0;

    if ( ! MONSTER.Common.getWordSet(this))
    {
        MONSTER.Common.showCursor();
        return MONSTER.Common.endScreen(this);
    }

    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x = (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit)
    {
        // not the first round

        this.game.tweens.push(new MONSTER.Tween(this.box.box, 'position.x', this.result_screen_x.left, 1000));
        setTimeout(this.activateShipAgain.bind(this), 1500);
    }

    this.game.tweens.push(new MONSTER.Tween(this.top_bar, 'position.y', this.top_bar_y.show, 1000));
    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.ShooterGame.prototype.activateShipAgain = function()
{
    this.shipActive = true;
};

MONSTER.ShooterGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);

    var max_size = 150;
    MONSTER.Common.secure_answer_size(text, sizes, max_size);

    var add = function()
    {
        text.position.x = 1 * Math.floor(Math.random() * r.width + r.x) + 1.3 * this.game.width;
        text.position.y = Math.floor(Math.random() * r.height + r.y);

        text.anchor.x = text.anchor.y = 0.5;
        context.game.view.addChild(text);

        var item_ = {
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);
    };

    add();
};

MONSTER.Game = function(fps)
{
    this.requestId = undefined;

    // Possible resolutions
    this.res = [
        [800, 450]
    ];

    this.games = window.games;
    this.current_game = '';

    this.pause = false;

    this.anon_game = true;

    // games temps

    this.game_tmp = {};

    // When we request words from a data set, we are sent a number of
    // sets (e.g. 10) with different words in each level.
    // Here, we store which level is the current one.
    this.level_id = 0;

    this.max_rounds = 20;

    for (var i = 0; i < this.games.length; i++) {
        this.game_tmp[game] = null;
    }

    this.data = window.data;
    this.initStage();

    MONSTER.initFonts(
        [MONSTER.Const.DEFAULT_FONT_FAMILY],
        [
            MONSTER.Const.COLOURS["navy"],
            MONSTER.Const.COLOURS["white"]
        ],
        ["36", "30", "26", "22", "16", "12"]
    );

    // array of all tweens
    this.tweens = [];

    this.assets = {
        'simple': {},
        'runner': {
            'runner_run': '/static/images/games/runner/panda_run.png',
            'runner_jump': '/static/images/games/runner/panda_jump.png',
            'runner_far_background': '/static/images/games/runner/far_background.png',
            'runner_background': '/static/images/games/runner/background.png',
            'runner_trees': '/static/images/games/runner/trees.png',
            'runner_foreground': '/static/images/games/runner/foreground.png',
            'runner_ground': '/static/images/games/runner/ground.png'
        },
        'shooter': {
            'shooter_background' : '/static/images/games/shooter/background.png',
            'shooter_clouds' : '/static/images/games/shooter/clouds.png',
            'shooter_middle' : '/static/images/games/shooter/middle.png',
            'shooter_foreground' : '/static/images/games/shooter/foreground.png',
            'shooter_snowball' : '/static/images/games/shooter/snowball.png',
            'shooter_crosshair' : '/static/images/games/shooter/crosshair.png'
        },
        'plane': {
            'plane_sky': '/static/images/games/plane/sky.png',
            'plane_background': '/static/images/games/plane/background.png',
            'plane_hills': '/static/images/games/plane/hills.png',
            'plane_valley': '/static/images/games/plane/valley.png',
            'plane_plane': '/static/images/games/plane/crazy_plane.png'
        },
        'space': {
            'space_ocean': '/static/images/games/space/ocean.png',
            'space_clouds': '/static/images/games/space/clouds.png',
            'space_plane': '/static/images/games/space/plane.png',
            'space_plane_left': '/static/images/games/space/plane_left.png',
            'space_plane_right': '/static/images/games/space/plane_right.png'
        },
        'ui': {
            'ui_btn_info': '/static/images/games/information.png',
            'ui_btn_menu': '/static/images/games/menu.png',
            'ui_star': '/static/images/games/star.png',
            'ui_dark_star': '/static/images/games/dark_star.png'
        }
    };

    this.loaded = false;

    this.g = $("#game");
    this.g.focus();
    this.parent = this.g.parent();
    this.resolutionOK = false;

    if (window.canvas_only)
        this.renderer = new PIXI.CanvasRenderer(0, 0);
    else
        this.renderer = new PIXI.autoDetectRenderer(0, 0);

    this.resize();

    if (window.debug) {
        this.DEBUG = true;

        var sizes = MONSTER.getFonts(
            MONSTER.Const.DEFAULT_FONT_FAMILY,
            MONSTER.Const.COLOURS["white"]
        );

        this.debug = {
            'fps_text': new PIXI.Text("", sizes['16']),

            // Calculating average in last second
            'fps_ticks': 1,
            'fps': 0,
            'fps_timer': 0
        };

        this.debug['fps_text'].position.y = this.height - 18;

        this.top.addChild(this.debug['fps_text']);
    }


    // Last time when the frame was updated
    this.lastTime = Date.now();

    // Time since last frame was rendered [ms]
    this.timeSinceLastFrame = 0;

    // Current FPS that limits the rendering
    this.requestedFrameRate = 1000 / fps;

    window.addEventListener('orientationchange', this.resize.bind(this), false);
    window.addEventListener('resize', this.resize.bind(this), false);

    this.isWebGL = (this.renderer instanceof PIXI.WebGLRenderer) ? true : false;

    document.getElementById('game').appendChild(this.renderer.view);

    this.initRandomGame();
};

MONSTER.Game.prototype.constructor = MONSTER.Game;

MONSTER.Game.prototype.setStopFunc = function(func, time, bind) {
    this.stopTimer = 0;
    this.stopFunc = func;
    this.stopTime = time;
    this.stopBind = bind;
};

MONSTER.Game.prototype.resetStopFunc = function() {
    this.stopTimer = 0;
    this.stopFunc = null;
    this.stopTime = 0;
    this.stopBind = null;
};

MONSTER.Game.prototype.kick_off = function() {
    this.stop();

    var id = Math.floor(Math.random() * this.games.length);
    var game = this.games[id];
    this.current_game = game;

    if (game == 'simple')
        this.currentScreen = new MONSTER.SimpleGame(this);
    else if (game == 'space')
        this.currentScreen = new MONSTER.SpaceGame(this);
    else if (game == 'plane')
        this.currentScreen = new MONSTER.PlaneGame(this);
    else if (game == 'runner')
        this.currentScreen = new MONSTER.RunnerGame(this);
    else if (game == 'shooter')
        this.currentScreen = new MONSTER.ShooterGame(this);

    this.start();
};

MONSTER.Game.prototype.initRandomGame = function()
{
    this.stop();
    this.current_game = game;

    this.currentScreen = new MONSTER.LoadingScreen(this);

    // start drawing
    this.start();
};

MONSTER.Game.prototype.initStage = function()
{
    this.stage = new PIXI.Container();

    this.background = new PIXI.Graphics();
    this.top = new PIXI.Graphics();
    this.view = new PIXI.Container();

    this.stage.addChild(this.background);
    this.stage.addChild(this.view);
    this.stage.addChild(this.top);
};

MONSTER.Game.prototype.next_level = function() {
    var word_sets = this.word_sets.data;
    var words_sets_cnt = word_sets.length;

    if ((this.level_id + 1) == words_sets_cnt) {
        this.level_id = 0;
    }

    this.to_ask = word_sets[this.level_id].to_ask.slice();
    this.all = this.to_ask.slice();

    this.rounds = this.to_ask.length;
    this.actual_rounds = Math.min(this.rounds, this.max_rounds);

    this.points = 0;

    this.round_id = 0;

    this.to_repeat = [];
    this.learned = [];
};

MONSTER.Game.prototype.resize = function()
{
    this.resolutionOK = false;
    var width = this.parent.width();

    // Size of the game screen
    this.width = 0;
    this.height = 0;

    for (var i = 0; i < this.res.length; i++)
    {
        var w = this.res[i][0];
        var h = this.res[i][1];

        if (w < width)
        {
            this.width = w;
            this.height = h;
            this.resolutionOK = true;
            break;
        }
    }

    // Scale
    this.scaleX = this.width / 800;
    this.scaleY = this.height / 450;
    this.view.scale.x = this.scaleX;
    this.view.scale.y = this.scaleY;
    this.background.scale.x = this.scaleX;
    this.background.scale.y = this.scaleY;

    if (this.resolutionOK)
    {
        $("#alert-browser-size").hide();
        this.renderer.resize(this.width, this.height);
    }
    else
    {
        $("#alert-browser-size").show();
        this.renderer.resize(0, 0);
    }
};

MONSTER.Game.prototype.frameRate = function()
{
    var now = Date.now();
    this.timeSinceLastFrame = now - this.lastTime;
    this.lastTime = now;
};

MONSTER.Game.prototype.update = function()
{
    if (this.currentScreen && ! this.pause)
    {
        this.currentScreen.update();

        for (var i = 0; i < this.tweens.length; i++)
        {
            this.tweens[i].update(this.timeSinceLastFrame);
        }

        if (this.stopFunc) {
            this.stopTimer += this.timeSinceLastFrame;

            if (this.stopTimer > this.stopTime) {
                this.stopFunc.call(this.stopBind);
                this.resetStopFunc();
            }
        }
    }
};

MONSTER.Game.prototype.start = function()
{
    if (this.requestId === undefined)
    {
        this.draw();
    }
};

MONSTER.Game.prototype.stop = function()
{
    if (this.requestId !== undefined)
    {
        MONSTER.Common.cancelAnimationFrame(this.requestId);
        this.requestId = undefined;
    }
};

MONSTER.Game.prototype.draw = function()
{
    if (this && this.renderer) {
        this.update();
        this.renderer.render(this.stage);
        this.frameRate();
    }

    this.requestId = requestAnimationFrame(this.draw.bind(this));
};

var game = null;

MONSTER.newGame = function() {
    game = new MONSTER.Game(60);
};

window.onload = function() {
    if (window.play)
        MONSTER.newGame();
};
