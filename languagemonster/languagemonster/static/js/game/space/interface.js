
MONSTER.SpaceGame.prototype.moveOutOfScreen = function()
{
    // question

    this.game.tweens.push(new MONSTER.Tween(this.top_bar, 'position.y', this.top_bar_y.hide, 1000));

    // answers

    for (var i = 0; i < this.answers.length; i++)
    {
        var obj = this.answers[i];

        if (obj.text.position.x < this.game.width / 2.0)
            this.game.tweens.push(new MONSTER.Tween(obj.text, 'position.x', - obj.text.width / 2, 1000));
        else
            this.game.tweens.push(new MONSTER.Tween(obj.text, 'position.x', this.game.width + obj.text.width / 2, 1000));
    }
};

MONSTER.SpaceGame.prototype.resultScreen = function(is_correct)
{
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.SpaceGame.prototype.next_round = function()
{
    this.answers.length = 0;
    var ctx = this;

    if ( ! MONSTER.Common.getWordSet(this))
    {
        return MONSTER.Common.endScreen(this);
    }

    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x = (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit)
    {
        // not the first round

        this.game.tweens.push(new MONSTER.Tween(this.box.box, 'position.x', this.result_screen_x.left, 1000));
        setTimeout(function() {
            ctx.activateShipAgain();
        }, 1500);
    }

    this.game.tweens.push(new MONSTER.Tween(this.top_bar, 'position.y', this.top_bar_y.show, 1000));
    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.SpaceGame.prototype.activateShipAgain = function()
{
    this.shipActive = true;
    this.ship.alpha = 1.0;
    // this.ship.tint = 0xffffff;
};

MONSTER.SpaceGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];
    var tmp = new PIXI.Graphics();

    var rx = Math.floor(Math.random() * r.width + r.x);
    var ry = Math.floor(Math.random() * r.height + r.y);

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);

    MONSTER.Common.secure_answer_size(text, sizes, 150);

    var add = function()
    {
        if (rx < context.game.width / 2.0)
            text.position.x = -text.width;
        else
            text.position.x = context.game.width + text.width;

        text.position.y = ry;
        text.anchor.x = text.anchor.y = 0.5;
        context.game.view.addChild(text);

        var rect_ = new PIXI.Rectangle(rx - text.width / 2, text.position.y - text.height / 2, text.width, text.height);
        var item_ = {
            'r' : rect_,
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);

        context.game.tweens.push(new MONSTER.Tween(text, 'position.x', rx, 1000));
    };

    add();
};
