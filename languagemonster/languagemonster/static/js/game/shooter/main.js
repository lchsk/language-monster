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
