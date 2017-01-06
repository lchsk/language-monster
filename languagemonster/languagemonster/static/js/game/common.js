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
    // Go on to the next level with <enter>
    MONSTER.Common._continue_handler = function(event) {
        MONSTER.Common.keyup_handler(event, context.game);
    };

    document.addEventListener('keyup', MONSTER.Common._continue_handler, false);

    // Show the "Continue" button
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

        // sprites.lenght must be 2
        var sprite_left = sprites[0];
        var sprite_right = sprites[1];

        if (sprites[1].position.x < sprites[0].position.x) {
            sprite_right = sprites[0];
            sprite_left = sprites[1];
        }

        sprite_left.position.x -= speed * delta;
        sprite_right.position.x = sprite_left.position.x + width;

        if (sprite_left.position.x <= -width) {
            var shifted_bg = sprites.shift();

            shifted_bg.position.x = sprite_right.position.x + width;

            sprites.push(shifted_bg);
        }
    }
};

MONSTER.GoodWrongScreen = function(game, result_screen_x, result_screen_pos)
{
    var box = new PIXI.Container();

    var pos_screen = new PIXI.Graphics();
    var pos_screen_success = new PIXI.Graphics();

    pos_screen_success.beginFill(game.currentScreen.colors.success, 0.8);
    pos_screen_success.drawRect(
        result_screen_x.show,
        result_screen_pos.y,
        result_screen_pos.width,
        result_screen_pos.height
    );
    pos_screen_success.endFill();

    var pos_screen_failure = new PIXI.Graphics();
    pos_screen_failure.beginFill(game.currentScreen.colors.failure, 0.8);
    pos_screen_failure.drawRect(
        result_screen_x.show,
        result_screen_pos.y,
        result_screen_pos.width,
        result_screen_pos.height
    );
    pos_screen_failure.endFill();

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

    box.addChild(pos_screen_failure);
    box.addChild(pos_screen_success);
    box.addChild(pos_screen);
    pos_screen.addChild(pos_screen_text);
    pos_screen.addChild(pos_screen_comment);
    pos_screen.addChild(pos_screen_text_line1);
    pos_screen.addChild(pos_screen_text_line2);
    pos_screen.addChild(pos_screen_text_line3);

    return {
        box: box,
        pos_screen: pos_screen,
        pos_screen_success: pos_screen_success,
        pos_screen_failure: pos_screen_failure,
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

    box.pos_screen_success.visible = is_correct;
    box.pos_screen_failure.visible = ! is_correct;

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
