MONSTER.PlaneGame = function(game)
{
    var that = this;
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

    this.sizes = {
        '36' : { font: "36px Montserrat", fill: "white" },
        '30' : { font: "30px Montserrat", fill: "white" },
        '26' : { font: "26px Montserrat", fill: "white" },
        '22' : { font: "22px Montserrat", fill: "white" },
        '16' : { font: "16px Montserrat", fill: "white" },
        '12' : { font: "12px Montserrat", fill: "white" }
    };

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

    this.urls = {
      'plane1' : '/static/images/games/plane/planeRed1.png',
      'plane2' : '/static/images/games/plane/planeRed2.png',
      'plane3' : '/static/images/games/plane/planeRed3.png'
    };

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

    if ( ! this.hit)
    {
        this.moveShip();

        if (this.answers && this.game.actual_rounds)
        {
            var t = this.game.timeSinceLastFrame;

            for (var i = 0; i < this.answers.length; i++)
            {
                if (this.constant_answer_speed)
                {
                    this.answers[i].text.position.x -= t * 0.14;
                }
                else
                {
                    this.answers[i].text.position.x -=
                        MONSTER.linear(
                            this.game.round_id,
                            0,
                            this.game.actual_rounds - 1,
                            0.08,
                            0.1
                        ) * t;
                }
            }
        }

        if (this.shipActive)
            this.checkCollisions();
    }
};

MONSTER.PlaneGame.prototype.init = function()
{
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    var textures = [];
    textures.push(PIXI.Texture.fromImage(this.urls.plane1));
    textures.push(PIXI.Texture.fromImage(this.urls.plane2));
    textures.push(PIXI.Texture.fromImage(this.urls.plane3));

    this.ship = new PIXI.extras.MovieClip(textures);
    this.ship.animationSpeed = 0.3;
    this.ship.scale.x = this.ship.scale.y = 0.7;
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
