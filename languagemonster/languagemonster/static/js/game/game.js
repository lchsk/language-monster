MONSTER.Game = function(fps)
{
    this.requestId = undefined;

    // Possible resolutions
    this.res = [
        [800, 450]
    ];

    this.games = window.games;
    this.current_game = '';

    this.pause = false;

    this.anon_game = true;

    // games temps

    this.game_tmp = {};

    // When we request words from a data set, we are sent a number of
    // sets (e.g. 10) with different words in each level.
    // Here, we store which level is the current one.
    this.level_id = 0;

    this.max_rounds = 20;

    for (var i = 0; i < this.games.length; i++) {
        this.game_tmp[game] = null;
    }

    this.data = window.data;
    this.initStage();

    MONSTER.initFonts(
        [MONSTER.Const.DEFAULT_FONT_FAMILY],
        [
            MONSTER.Const.COLOURS["navy"],
            MONSTER.Const.COLOURS["white"]
        ],
        ["36", "30", "26", "22", "16", "12"]
    );

    // array of all tweens
    this.tweens = [];

    this.assets = {
        'simple': {},
        'runner': {
            'runner_run': '/static/images/games/runner/panda_run.png',
            'runner_jump': '/static/images/games/runner/panda_jump.png',
            'runner_far_background': '/static/images/games/runner/far_background.png',
            'runner_background': '/static/images/games/runner/background.png',
            'runner_trees': '/static/images/games/runner/trees.png',
            'runner_foreground': '/static/images/games/runner/foreground.png',
            'runner_ground': '/static/images/games/runner/ground.png'
        },
        'shooter': {
            'shooter_background' : '/static/images/games/shooter/background.png',
            'shooter_clouds' : '/static/images/games/shooter/clouds.png',
            'shooter_middle' : '/static/images/games/shooter/middle.png',
            'shooter_foreground' : '/static/images/games/shooter/foreground.png',
            'shooter_snowball' : '/static/images/games/shooter/snowball.png',
            'shooter_crosshair' : '/static/images/games/shooter/crosshair.png'
        },
        'plane': {
            'plane_sky': '/static/images/games/plane/sky.png',
            'plane_background': '/static/images/games/plane/background.png',
            'plane_hills': '/static/images/games/plane/hills.png',
            'plane_valley': '/static/images/games/plane/valley.png',
            'plane_plane': '/static/images/games/plane/crazy_plane.png'
        },
        'space': {
            'space_ocean': '/static/images/games/space/ocean.png',
            'space_clouds': '/static/images/games/space/clouds.png',
            'space_plane': '/static/images/games/space/plane.png',
            'space_plane_left': '/static/images/games/space/plane_left.png',
            'space_plane_right': '/static/images/games/space/plane_right.png'
        },
        'ui': {
            'ui_btn_info': '/static/images/games/information.png',
            'ui_btn_menu': '/static/images/games/menu.png',
            'ui_star': '/static/images/games/star.png',
            'ui_dark_star': '/static/images/games/dark_star.png'
        }
    };

    this.loaded = false;

    this.g = $("#game");
    this.g.focus();
    this.parent = this.g.parent();
    this.resolutionOK = false;

    if (window.canvas_only)
        this.renderer = new PIXI.CanvasRenderer(0, 0);
    else
        this.renderer = new PIXI.autoDetectRenderer(0, 0);

    this.resize();

    if (window.debug) {
        this.DEBUG = true;

        var sizes = MONSTER.getFonts(
            MONSTER.Const.DEFAULT_FONT_FAMILY,
            MONSTER.Const.COLOURS["white"]
        );

        this.debug = {
            'fps_text': new PIXI.Text("", sizes['16']),

            // Calculating average in last second
            'fps_ticks': 1,
            'fps': 0,
            'fps_timer': 0
        };

        this.debug['fps_text'].position.y = this.height - 18;

        this.top.addChild(this.debug['fps_text']);
    }


    // Last time when the frame was updated
    this.lastTime = Date.now();

    // Time since last frame was rendered [ms]
    this.timeSinceLastFrame = 0;

    // Current FPS that limits the rendering
    this.requestedFrameRate = 1000 / fps;

    window.addEventListener('orientationchange', this.resize.bind(this), false);
    window.addEventListener('resize', this.resize.bind(this), false);

    this.isWebGL = this.renderer instanceof PIXI.WebGLRenderer;

    document.getElementById('game').appendChild(this.renderer.view);

    this.initRandomGame();
};

MONSTER.Game.prototype.constructor = MONSTER.Game;

MONSTER.Game.prototype.setStopFunc = function(func, time, bind) {
    this.stopTimer = 0;
    this.stopFunc = func;
    this.stopTime = time;
    this.stopBind = bind;
};

MONSTER.Game.prototype.resetStopFunc = function() {
    this.stopTimer = 0;
    this.stopFunc = null;
    this.stopTime = 0;
    this.stopBind = null;
};

MONSTER.Game.prototype.kick_off = function() {
    this.stop();

    var id = Math.floor(Math.random() * this.games.length);
    var game = this.games[id];
    this.current_game = game;

    this.initStage();

    if (game == 'simple')
        this.currentScreen = new MONSTER.SimpleGame(this);
    else if (game == 'space')
        this.currentScreen = new MONSTER.SpaceGame(this);
    else if (game == 'plane')
        this.currentScreen = new MONSTER.PlaneGame(this);
    else if (game == 'runner')
        this.currentScreen = new MONSTER.RunnerGame(this);
    else if (game == 'shooter')
        this.currentScreen = new MONSTER.ShooterGame(this);

    this.start();
};

MONSTER.Game.prototype.initRandomGame = function()
{
    this.stop();
    this.current_game = game;

    this.currentScreen = new MONSTER.LoadingScreen(this);

    // start drawing
    this.start();
};

MONSTER.Game.prototype.initStage = function()
{
    this.stage = new PIXI.Container();

    this.background = new PIXI.Graphics();
    this.top = new PIXI.Graphics();
    this.view = new PIXI.Container();

    this.stage.addChild(this.background);
    this.stage.addChild(this.view);
    this.stage.addChild(this.top);
};

MONSTER.Game.prototype.next_level = function() {
    var word_sets = this.word_sets.data;
    var words_sets_cnt = word_sets.length;

    if ((this.level_id + 1) == words_sets_cnt) {
        this.level_id = 0;
    }

    this.to_ask = word_sets[this.level_id].to_ask.slice();
    this.all = this.to_ask.slice();

    this.rounds = this.to_ask.length;
    this.actual_rounds = Math.min(this.rounds, this.max_rounds);

    this.points = 0;

    this.round_id = 0;

    this.to_repeat = [];
    this.learned = [];
};

MONSTER.Game.prototype.resize = function()
{
    this.resolutionOK = false;
    var width = this.parent.width();

    // Size of the game screen
    this.width = 0;
    this.height = 0;

    for (var i = 0; i < this.res.length; i++)
    {
        var w = this.res[i][0];
        var h = this.res[i][1];

        if (w < width)
        {
            this.width = w;
            this.height = h;
            this.resolutionOK = true;
            break;
        }
    }

    // Scale
    this.scaleX = this.width / 800;
    this.scaleY = this.height / 450;
    this.view.scale.x = this.scaleX;
    this.view.scale.y = this.scaleY;
    this.background.scale.x = this.scaleX;
    this.background.scale.y = this.scaleY;

    $(".alert").hide();

    if (this.resolutionOK)
    {
        $("#alert-browser-size").hide();
        this.renderer.resize(this.width, this.height);
    }
    else
    {
        $("#alert-browser-size").show();
        this.renderer.resize(0, 0);
    }
};

MONSTER.Game.prototype.frameRate = function()
{
    var now = Date.now();
    this.timeSinceLastFrame = now - this.lastTime;
    this.lastTime = now;
};

MONSTER.Game.prototype.update = function()
{
    if (this.currentScreen && ! this.pause)
    {
        this.currentScreen.update();

        for (var i = 0; i < this.tweens.length; i++)
        {
            this.tweens[i].update(this.timeSinceLastFrame);
        }

        if (this.stopFunc) {
            this.stopTimer += this.timeSinceLastFrame;

            if (this.stopTimer > this.stopTime) {
                this.stopFunc.call(this.stopBind);
                this.resetStopFunc();
            }
        }
    }
};

MONSTER.Game.prototype.start = function()
{
    if (this.requestId === undefined)
    {
        this.draw();
    }
};

MONSTER.Game.prototype.stop = function()
{
    if (this.requestId !== undefined)
    {
        MONSTER.Common.cancelAnimationFrame(this.requestId);
        this.requestId = undefined;
    }
};

MONSTER.Game.prototype.draw = function()
{
    if (this && this.renderer) {
        this.update();
        this.renderer.render(this.stage);
        this.frameRate();
    }

    this.requestId = requestAnimationFrame(this.draw.bind(this));
};

var game = null;

MONSTER.newGame = function() {
    game = new MONSTER.Game(60);
};

window.onload = function() {
    if (window.play)
        MONSTER.newGame();
};
