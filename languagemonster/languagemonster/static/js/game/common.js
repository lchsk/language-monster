MONSTER.Common = function(){};

MONSTER.Common.restart = function(obj)
{

};

MONSTER.Common.correct = function(game_screen)
{
    game_screen.game.learned.push(game_screen.wordpair_id);

    // Add points only if the question was asked the first time
    if (game_screen.game.round_id <= game_screen.game.actual_rounds) {
        game_screen.game.points++;
    }

    game_screen.resultScreen(true);
};

MONSTER.Common.negative = function(game_screen)
{
    game_screen.game.to_repeat.push(game_screen.wordpair_id);

    game_screen.game.to_ask.push([game_screen.question, game_screen.answer]);

    game_screen.resultScreen(false);
};

MONSTER.Common.check_answer = function(game, answer)
{
    if (answer === game.answer)
        MONSTER.Common.correct(answer);
    else
        MONSTER.Common.negative(answer);
};

MONSTER.Common.endScreen = function(obj)
{
    // End Level Screen (showing results)

    var context = obj;
    obj.game.view.removeChildren();

    obj.game.pct = Math.round(obj.game.points / obj.game.all.length * 100);
    var text = new PIXI.Text(obj.game.pct + '%', obj.sizes['36']);
    text.position.x = (obj.game.width - text.width) / 2;
    text.position.y = 0.35 * obj.game.height;

    var comment = new PIXI.Text("", obj.sizes['30']);
    comment.text = MONSTER.Common.trans("Well done", window.translations);
    comment.position.x = (obj.game.width - comment.width) / 2;
    comment.position.y = 0.15 * obj.game.height;

    obj.info = new PIXI.Text(
        MONSTER.Common.trans(
            "Sending results...",
            window.translations
        ),
        obj.sizes['16']
    );
    obj.info.position.x = (obj.game.width - obj.info.width) / 2;
    obj.info.position.y = 0.89 * obj.game.height;

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
            context.game.level_id++;
            context.game.next_level();
            context.game.kick_off();
        }
    );

    obj.game.view.addChild(text);
    obj.game.view.addChild(comment);
    obj.game.view.addChild(obj.info);

    obj.game.view.addChild(obj.b);
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

    game_screen.question = pair.words[dir_q];
    game_screen.answer = pair.words[dir_a];
    game_screen.wordpair_id = pair.id;

    game_screen.choices = [];
    game_screen.choices.push(game_screen.answer);

    shuffle(game.all);

    for (var i = 0; i < 4; i++) {
        if (game.all[i].id != game_screen.wordpair_id) {
            game_screen.choices.push(game.all[i].words[dir_a]);
        }
    }

    game_screen.choices = shuffle(game_screen.choices);

    if (game_screen.choices.length != 4) {
        throw "Not enough choices";
    }

    return true;
};

MONSTER.Common.spriteURLs = {
    'btn_info' : '/static/images/games/information.png'
};

MONSTER.Common.getLoader = function()
{
    var loader = PIXI.loader;
    loader.reset();
    loader.add('btn_info', MONSTER.Common.spriteURLs.btn_info);

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
    var btn_info = PIXI.Sprite.fromImage(MONSTER.Common.spriteURLs.btn_info);
    btn_info.scale.x = btn_info.scale.y = 0.65;
    btn_info.interactive = true;

    if ( ! game.currentScreen)
        return;

    var tutorial_id = game.tutorial;

    btn_info.click = function(d)
    {
        MONSTER.Common._showTutorial(game, tutorial_id);
    };

    btn_info.mouseover = function(d)
    {
        document.body.style.cursor = 'pointer';
    };

    btn_info.mouseout = function(d)
    {
        document.body.style.cursor = 'default';
    };

    $('#' + tutorial_id).on('hide.bs.modal', function(){
        game.pause = false;
        game.currentScreen.onGamePauseOff();
    });

    game.view.addChild(btn_info);
};

MONSTER.Common.fillBackground = function(obj, color)
{
    obj.game.background.beginFill(color, 1);
    obj.game.background.drawRect(0, 0, obj.game.width, obj.game.height);
    obj.game.background.endFill();
};

MONSTER.Common.setUpAjax = function()
{
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url)
                  || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
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

    var sizes = [
        context.sizes['26'],
        context.sizes['22'],
        context.sizes['16'],
        context.sizes['12']
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

    b.click = function(d)
    {
        b.clear();
        b.beginFill(context.button_colors.click);
        b.drawRect(x, y, width, height, 3);
        b.endFill();
        onclick();
    };

    b.mouseover = function(d)
    {
        b.clear();
        b.beginFill(context.button_colors.hover);
        b.drawRect(x, y, width, height, 3);
        b.endFill();
        document.body.style.cursor = 'pointer';
    };

    b.mouseout = function(d)
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
    })
    .success(function(msg)
    {
        obj.info.text = MONSTER.Common.trans(
            "Results were sent",
            window.translations);
        obj.info.position.x = (obj.game.width - obj.info.width) / 2;
        obj.b.interactive = true;
    })
    .error(function(msg)
    {
        obj.info.text = MONSTER.Common.trans(
            "Error when sending results",
            window.translations);
        obj.info.position.x = (obj.game.width - obj.info.width) / 2;
    });
};

MONSTER.Common.trans = function(word, d)
{
    if (word in d)
        return d[word];
    return word;
};

MONSTER.GoodWrongScreen = function(game, result_screen_x,
                                   result_screen_pos, sizes) {
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

        console.log(box);
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
