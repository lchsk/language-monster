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
