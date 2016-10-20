MONSTER.SpaceGame = function(game)
{
    var that = this;
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
        // 'ship' : '/static/images/games/space/ship.png'
      'ship1' : '/static/images/games/plane/planeRed1.png',
      'ship2' : '/static/images/games/plane/planeRed2.png',
      'ship3' : '/static/images/games/plane/planeRed3.png',
      'plane' : '/static/images/games/space/plane.png'
    };

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

    this.assets = objectValues(this.urls);

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

    if ( ! this.hit)
    {
        this.moveShip();

        if (this.shipActive)
            this.checkCollisions();
    }
};

MONSTER.SpaceGame.prototype.init = function()
{
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    var plane = PIXI.BaseTexture.fromImage(this.urls.plane);

    var textures = [];

    var FRAME_SIZE = 78;
    var FRAMES = 6;

    for (var i = 0; i < FRAMES; i++) {
        textures.push(new PIXI.Texture(
            plane,
            new PIXI.Rectangle(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
        ));
    }

    this.ship = new PIXI.extras.MovieClip(textures);
    this.ship.animationSpeed = 0.5;
    this.ship.play();
    this.game.view.addChild(this.ship);

    this.ship.anchor.x = 0.5;
    this.ship.anchor.y = 0.5;
    this.ship.position.x = this.game.width / 1.3;
    this.ship_v = 3;
    this.ship.rotation = Math.PI;

    this.game.view.addChild(this.top_bar);


    this.box.box.position.x = this.result_screen_x.right;

    MONSTER.Common.addUI(this.game);
    this.game.view.addChild(this.box.box);
    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};
