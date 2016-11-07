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
