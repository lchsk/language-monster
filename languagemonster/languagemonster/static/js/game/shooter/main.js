MONSTER.ShooterGame = function(game)
{
    var that = this;
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

    // True durign processing of a hit
    this.hit = false;

    // After hit ship is inactive for a while
    this.shipActive = true;

    this.constant_answer_speed = false;

    this.sizes = {
        '36': {fontFamily: "Montserrat", fontSize: 36, fill: "white"},
        '30': {fontFamily: "Montserrat", fontSize: 30, fill: "white"},
        '26': {fontFamily: "Montserrat", fontSize: 26, fill: "white"},
        '22': {fontFamily: "Montserrat", fontSize: 22, fill: "white"},
        '16': {fontFamily: "Montserrat", fontSize: 16, fill: "white"},
        '12': {fontFamily: "Montserrat", fontSize: 12, fill: "white"}
    };

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
        this.result_screen_pos,
        this.sizes
    );

    this.top_bar = new PIXI.Container();
    this.top_bar_text = new PIXI.Text("", this.sizes['36']);

    this.top_bar_y = {
      'show' : 0.18 * this.game.height,
      'hide' : - this.top_bar_text.height
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

    this.assets = objectValues(this.urls);

    this.init();
};

MONSTER.ShooterGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.ShooterGame.prototype.constructor = MONSTER.ShooterGame;

MONSTER.ShooterGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);

    if ( ! this.hit)
    {
        this.moveShip();

        if (this.answers && this.game.actual_rounds)
        {
            var left = 0;
            var t = this.game.timeSinceLastFrame;

            for (var i = 0; i < this.answers.length; i++)
            {
                if (this.constant_answer_speed)
                {
                    this.answers[i].text.position.x -= t * 0.16;
                }
                else
                {
                    this.answers[i].text.position.x -=
                        MONSTER.linear(
                            this.game.round_id,
                            0,
                            this.game.actual_rounds - 1,
                            0.16,
                            0.19
                        ) * t;
                }

                if (this.answers[i].text.position.x < this.answers[i].text.width / 2)
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

    this.ship.position.x = MONSTER.linear(
        this.crosshair.position.x,
        0,
        this.game.width,
        this.game.width * 0.4, this.game.width * 0.6
    );
};

MONSTER.ShooterGame.prototype.init = function()
{
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.hideCursor();

    MONSTER.Common.fillBackground(this, this.colors.background);

    this.crosshair_t = PIXI.Texture.fromImage(this.urls.crosshair);
    this.crosshair_red_t = PIXI.Texture.fromImage(this.urls.crosshair_red);

    this.crosshair = new PIXI.Sprite(this.crosshair_t);
    this.crosshair.anchor.x = this.crosshair.anchor.y = 0.5;
    this.crosshair.position.x = this.game.width * 0.5;
    this.crosshair.position.y = this.game.height * 0.5;


    this.ship = PIXI.Sprite.fromImage(this.urls.rifle);

    this.game.view.interactive = true;
    this.game.view.on('mousemove', this.mousemove.bind(this));
    this.game.view.on('mouseup', function(){
        context.crosshair.texture = context.crosshair_t;
    });
    this.game.view.on('mousedown', function(){
        context.crosshair.texture = context.crosshair_red_t;
    });


    this.game.view.on('click', this.checkHit.bind(this));

    this.ship.anchor.x = 0.5;
    this.ship.anchor.y = 0.5;
    this.ship.scale.x = this.ship.scale.y = 0.5;

    var stop_y = 0.56 * this.game.height;
    var start_y = 0.71 * this.game.height;

    this.original_y = 0.71 * this.game.height;
    this.slide_y = 0.78 * this.game.height;
    this.slide_t = 0;

    this.ship.position.x = 0.5 * this.game.width;
    this.ship.position.y = 0.9 * this.game.height;

    this.ship.start_y = start_y;
    this.ship.stop_y = stop_y;
    this.ship.v_time = 0;

    this.ship.v_up = false;
    this.ship.v_down = false;

    this.game.view.addChild(this.top_bar);


    this.box.box.position.x = this.result_screen_x.right;

    var grass1 = PIXI.Texture.fromImage(this.urls.grass1);
    var grass2 = PIXI.Texture.fromImage(this.urls.grass2);

    for (var i = 0, p = 0; i < this.game.width; i += 132, p++)
    {
        var s_grass;

        if (p % 2 === 0)
        {
            s_grass = new PIXI.Sprite(grass1);
            s_grass.position.y = this.game.height - 170;
        }
        else {
            s_grass = new PIXI.Sprite(grass2);
            s_grass.position.y = this.game.height - 186;
        }

        s_grass.position.x = i;

        this.game.view.addChild(s_grass);
    }

    this.game.view.addChild(this.ship);
    this.game.view.addChild(this.crosshair);
    MONSTER.Common.addUI(this.game);

    this.game.view.addChild(this.box.box);

    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};
