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

    this.sizes = {
        '36' : { font: "36px Montserrat", fill: "white" },
        '30' : { font: "30px Montserrat", fill: "white" },
        '26' : { font: "26px Montserrat", fill: "white" },
        '22' : { font: "22px Montserrat", fill: "white" },
        '16' : { font: "16px Montserrat", fill: "white" },
        '12' : { font: "12px Montserrat", fill: "white" }
    };

    MONSTER.Common.setUpAjax();

    this.data_loader = new MONSTER.DataLoader(
        this.game.data.dataset_id,
        this.game.data.email,
        this.max_rounds,
        this.start_loading,
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
      'y' : 0.5 * this.game.height - 0.5 * this.top_bar_text.height,
      'x' : 0.5 * this.game.width - 0.5 * this.top_bar_text.width
    };

    this.top_bar_loading_text_pos = {
      'y' : 0.7 * this.game.height - 0.5 * this.top_bar_loading_text.height,
      'x' : 0.5 * this.game.width - 0.5 * this.top_bar_loading_text.width
    };

    this.top_bar_text.position.y = this.top_bar_text_pos.y;
    this.top_bar_text.position.x = this.top_bar_text_pos.x;
    this.top_bar_loading_text.position.y = this.top_bar_loading_text_pos.y;
    this.top_bar_loading_text.position.x = this.top_bar_loading_text_pos.x;

    this.top_bar.addChild(this.top_bar_text);
    this.top_bar.addChild(this.top_bar_loading_text);
    this.top_bar.addChild(this.loading_bar);

    this.init();

    var avail_games = window.games;
    this.loader = MONSTER.Common.getLoader();

    for (var i = 0; i < avail_games.length; i++) {
        var game_assets = game.assets[avail_games[i]];
        for (var img in game_assets) {
            if (game_assets.hasOwnProperty(img)) {
                this.loader.add(img, game_assets[img]);
            }
        }
    }
    this.loader.on('progress', function() {
        that.loading_bar_pos_x = that.loader.progress / 100.0 * that.game.width;
    });
    this.loader.on('complete', function() {
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
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    this.game.view.addChild(this.top_bar);

};

MONSTER.LoadingScreen.prototype.kick_off = function() {
    this.game.kick_off();
};

MONSTER.RunnerGame = function(game)
{
    var that = this;
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

    this.sizes = {
        '36' : { font: "36px Montserrat", fill: "white" },
        '30' : { font: "30px Montserrat", fill: "white" },
        '26' : { font: "26px Montserrat", fill: "white" },
        '22' : { font: "22px Montserrat", fill: "white" },
        '16' : { font: "16px Montserrat", fill: "white" },
        '12' : { font: "12px Montserrat", fill: "white" }
    };

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
        'run': '/static/images/games/runner/panda_run.png',
        'jump': '/static/images/games/runner/panda_jump.png',
        'dirt' : '/static/images/games/runner/dirt.png',
        'dirt_grass' : '/static/images/games/runner/dirt_grass.png'
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

MONSTER.RunnerGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.RunnerGame.prototype.constructor = MONSTER.RunnerGame;

MONSTER.RunnerGame.prototype.update = function()
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
                {
                    this.answers[i].text.position.x -=
                        MONSTER.linear(
                            this.game.round_id,
                            0,
                            this.game.actual_rounds - 1,
                            0.2,
                            0.23
                        ) * t;
                }
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
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    this.textures = [];
    this.textures_jump = [];

    var FRAME_W = 88;
    var FRAME_RUN_H = 150;
    var FRAME_JUMP_H = 158;
    var FRAMES_RUN = 8;

    var panda_run = PIXI.BaseTexture.fromImage(this.urls.run);
    var panda_jump = PIXI.BaseTexture.fromImage(this.urls.jump);

    for (var i = 0; i < FRAMES_RUN; i++) {
        var rect_run = new PIXI.Rectangle(i * FRAME_W, 0, FRAME_W, FRAME_RUN_H);
        var rect_jump = new PIXI.Rectangle(i * FRAME_W, 0, FRAME_W, FRAME_JUMP_H);

        this.textures.push(new PIXI.Texture(panda_run, rect_run));
        this.textures_jump.push(new PIXI.Texture(panda_jump, rect_jump));
    }

    this.ship = new PIXI.extras.MovieClip(this.textures);
    this.ship.animationSpeed = 0.2;
    this.ship.play();

    this.ship.anchor.x = 0.5;
    this.ship.anchor.y = 0.5;

    var stop_y = 0.56 * this.game.height;
    var start_y = 0.71 * this.game.height;

    this.original_y = 0.71 * this.game.height;
    this.slide_y = 0.78 * this.game.height;
    this.slide_t = 0;

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

    var dirt_grass = PIXI.Texture.fromImage(this.urls.dirt_grass);

    for (var i = 0; i < this.game.width; i += 64)
    {
        var s_dirt_grass = new PIXI.Sprite(dirt_grass);
        s_dirt_grass.position.x = i;
        s_dirt_grass.position.y = this.game.height - 64;
        s_dirt_grass.scale.x = s_dirt_grass.scale.y = 0.5;
        this.game.view.addChild(s_dirt_grass);
    }

    this.game.view.addChild(this.ship);
    MONSTER.Common.addUI(this.game);
    this.game.view.addChild(this.box.box);

    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);

    this.next_round();
};
