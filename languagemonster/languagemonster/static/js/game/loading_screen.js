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
        '36': {fontFamily: "Montserrat", fontSize: 36, fill: "white"},
        '30': {fontFamily: "Montserrat", fontSize: 30, fill: "white"},
        '26': {fontFamily: "Montserrat", fontSize: 26, fill: "white"},
        '22': {fontFamily: "Montserrat", fontSize: 22, fill: "white"},
        '16': {fontFamily: "Montserrat", fontSize: 16, fill: "white"},
        '12': {fontFamily: "Montserrat", fontSize: 12, fill: "white"}
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
