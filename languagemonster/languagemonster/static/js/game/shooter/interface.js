
MONSTER.ShooterGame.prototype.moveOutOfScreen = function()
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

MONSTER.ShooterGame.prototype.resultScreen = function(is_correct)
{
    result_screen_on = true;
    // this.round_id++;
    MONSTER.GoodWrongScreen.prepare(this, is_correct);
};

MONSTER.ShooterGame.prototype.next_round = function()
{
    this.answers.length = 0;

    if ( ! MONSTER.Common.getWordSet(this))
    {
        MONSTER.Common.showCursor();
        return MONSTER.Common.endScreen(this);
    }

    this.top_bar_text.text = this.question;
    this.top_bar_text.position.x = (this.game.width - this.top_bar_text.width) / 2;

    if (this.hit)
    {
        // not the first round

        this.game.tweens.push(new MONSTER.Tween(this.box.box, 'position.x', this.result_screen_x.left, 1000));
        setTimeout(this.activateShipAgain.bind(this), 1500);
    }

    this.game.tweens.push(new MONSTER.Tween(this.top_bar, 'position.y', this.top_bar_y.show, 1000));
    this.createAnswer(this.choices[0], 0);
    this.createAnswer(this.choices[1], 1);
    this.createAnswer(this.choices[2], 2);
    this.createAnswer(this.choices[3], 3);

    this.hit = false;
};

MONSTER.ShooterGame.prototype.activateShipAgain = function()
{
    this.shipActive = true;
};

MONSTER.ShooterGame.prototype.createAnswer = function(t, id)
{
    var context = this;

    var r = this.rects[id];
    var tmp = new PIXI.Graphics();

    var sizes = [
        this.sizes['22'], this.sizes['16'], this.sizes['12']
    ];

    var sizeId = 0;

    var text = new PIXI.Text(t, sizes[sizeId]);

    var max_size = 150;
    MONSTER.Common.secure_answer_size(text, sizes, max_size);

    var add = function()
    {
        text.position.x = 1 * Math.floor(Math.random() * r.width + r.x) + 1.3 * this.game.width;
        text.position.y = Math.floor(Math.random() * r.height + r.y);

        text.anchor.x = text.anchor.y = 0.5;
        context.game.view.addChild(text);

        var item_ = {
            'word' : t,
            'text' : text
        };
        context.answers.push(item_);
    };

    add();
};
