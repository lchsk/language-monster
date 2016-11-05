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

    // After hit ship is inactive for a while
    this.shipActive = true;

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

    this.assets = objectValues(this.urls);

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

        if (this.shipActive)
            this.checkCollisions();
    }
};

MONSTER.PlaneGame.prototype.init = function()
{
    this.game.background.clear();
    this.game.view.removeChildren();

    var sky_t = PIXI.Texture.fromImage(this.urls.sky);
    var background_t = PIXI.Texture.fromImage(this.urls.background);
    var valley_t = PIXI.Texture.fromImage(this.urls.valley);
    var hills_t = PIXI.Texture.fromImage(this.urls.hills);

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

    var plane = PIXI.BaseTexture.fromImage(this.urls.plane);

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
