MONSTER.SimpleGame = function(game)
{
    MONSTER.AbstractScreen.call(this, game);
    var that = this;
    this.ID = 'simple';
    game.tutorial = 'modal-tut-simple';
    this.trans = window.translations;

    // ------------------
    // Settings
    // ------------------

    this.colors = {
        background: '0x243757',
        success: '0x33E46D',
        failure: '0xFF5039',

        question: '#ffffff',
        active: '0xC72618',
        hover: '0xAE0D00',
        click: '0x940000'
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

    // - end settings

    MONSTER.Common.setUpAjax();

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

    this.init();
};

MONSTER.SimpleGame.prototype = Object.create(MONSTER.AbstractScreen.prototype);
MONSTER.SimpleGame.prototype.constructor = MONSTER.SimpleGame;

MONSTER.SimpleGame.prototype.onGamePause = function()
{
};

MONSTER.SimpleGame.prototype.onGamePauseOff = function()
{
};

MONSTER.SimpleGame.prototype.update = function()
{
    MONSTER.AbstractScreen.prototype.update.call(this);
};

MONSTER.SimpleGame.prototype.next_round = function() {
    var ctx = this;

    setTimeout(function() {
        ctx.init();
    }, 100);

    this.game.tweens.push(
        new MONSTER.Tween(
            this.box.box,
            'position.x',
            this.result_screen_x.left,
            1000
        )
    );
};

MONSTER.SimpleGame.prototype.resultScreen = function(is_correct)
{
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.SimpleGame.prototype.check_answer = function(answer)
{
    if (answer === this.answer)
        MONSTER.Common.correct(this);
    else
        MONSTER.Common.negative(this);
};

MONSTER.SimpleGame.prototype.init = function()
{
    var context = this;
    this.game.background.clear();
    this.game.view.removeChildren();

    MONSTER.Common.fillBackground(this, this.colors.background);

    if ( ! MONSTER.Common.getWordSet(this))
    {
        return MONSTER.Common.endScreen(this);
    }

    var text = new PIXI.Text(
        this.question,
        {font: "36px Montserrat", fill: this.colors.question}
    );
    text.position.x = (this.game.width - text.width) / 2;
    text.position.y = 0.12 * this.game.height;
    this.game.view.addChild(text);

    var w = 250;
    var h = 90;
    var time = 1400;

    var b1 = MONSTER.Common.createButton(
        this,
        this.choices[0], 0, 0, w, h, -w, 150, function(){
        b1.interactive = false;
        context.check_answer(context.choices[0]);
    });
    b1.interactive = true;

    var b2 = MONSTER.Common.createButton(
        this,
        this.choices[1], 0, 0, w, h, this.game.width + w, 150, function(){
        b2.interactive = false;
        context.check_answer(context.choices[1]);
    });
    b2.interactive = true;

    var b3 = MONSTER.Common.createButton(
        this,
        this.choices[2], 0, 0, w, h, -w, 280, function(){
        b3.interactive = false;
        context.check_answer(context.choices[2]);
    });
    b3.interactive = true;

    var b4 = MONSTER.Common.createButton(
        this,
        this.choices[3], 0, 0, w, h, this.game.width + w, 280, function(){
        b4.interactive = false;
        context.check_answer(context.choices[3]);
    });
    b4.interactive = true;

    this.game.view.addChild(b1);
    this.game.view.addChild(b2);
    this.game.view.addChild(b3);
    this.game.view.addChild(b4);

    this.game.tweens.push(new MONSTER.Tween(b1, 'position.x', 75, time));
    this.game.tweens.push(new MONSTER.Tween(b2, 'position.x', 475, time));
    this.game.tweens.push(new MONSTER.Tween(b3, 'position.x', 75, time));
    this.game.tweens.push(new MONSTER.Tween(b4, 'position.x', 475, time));

    MONSTER.Common.addUI(this.game);
    this.box.box.position.x = this.result_screen_x.right;
    this.game.view.addChild(this.box.box);
    setTimeout(function(){ MONSTER.Common.showTutorial(this.game); }, 700);
};
