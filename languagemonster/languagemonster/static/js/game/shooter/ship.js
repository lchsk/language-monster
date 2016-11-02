MONSTER.ShooterGame.prototype.moveShip = function()
{
    if (this.snowball.thrown) {
        var snowball = this.snowball;
        var delta = this.game.timeSinceLastFrame;

        var sprite = snowball.sprite;

        sprite.position.x = snowball.pos[0];
        sprite.position.y = snowball.pos[1];

        snowball.time += delta;

        if (snowball.time < this.SNOWBALL_TIME) {
            var new_pos = MONSTER.Utils.bezier(
                snowball.time / this.SNOWBALL_TIME, [
                    {
                        'x': snowball.src[0],
                        'y': snowball.src[1]
                    },
                    {
                        'x': (snowball.src[0] + snowball.dest[0]) / 2.0,
                        'y': (snowball.src[1] + snowball.dest[1]) / 2.0
                    },
                    {
                        'x': snowball.dest[0],
                        'y': snowball.dest[1]
                    }
                ]
            );

            sprite.position.x = new_pos.x;
            sprite.position.y = new_pos.y;

            var scale = this.SNOWBALL_TIME / 2.0 / snowball.time;

            sprite.visible = scale < 4;
            sprite.scale.x = sprite.scale.y = scale;

            this.checkHit(sprite.position.x, sprite.position.y);
        } else
            this.resetSnowball(this.snowball);
    }
};

MONSTER.ShooterGame.prototype.resetSnowball = function(snowball)
{
    snowball.sprite.anchor.x = snowball.sprite.anchor.y = 0.5;
    snowball.src = [0, 0];
    snowball.pos = [0, 0];
    snowball.time = 0;
    snowball.thrown = false;
};

MONSTER.ShooterGame.prototype.throw = function()
{
    var snowball = this.snowball;

    if (! snowball.thrown) {
        snowball.thrown = true;

        var pos_x = MONSTER.linear(
            this.crosshair.position.x,
            0,
            this.game.width,
            this.game.width * 0.2, this.game.width * 0.8
        );

        var pos_y = this.game.height + snowball.sprite.height;

        snowball.src = [pos_x, pos_y];
        snowball.pos = [pos_x, pos_y];
        snowball.dest = [this.crosshair.position.x, this.crosshair.position.y];
    }
};

MONSTER.ShooterGame.prototype.checkHit = function(x, y)
{
    if (! this.hit) {
        for (var i = 0; i < this.answers.length; i++) {
            var obj = this.answers[i];

            if (MONSTER.Utils.isPointInRectWithTol(x, y, [
                obj.text.position.x,
                obj.text.position.y,
                obj.text.width,
                obj.text.height
            ], [100, 100])) {
                this.game.tweens.push(
                    new MONSTER.Tween(
                        obj.text,
                        'position.y',
                        -200,
                        1000
                    )
                );
                this.game.tweens.push(
                    new MONSTER.Tween(
                        obj.text,
                        'position.x',
                        MONSTER.Utils.getRandomInt(
                            0.2 * this.game.width,
                            0.8 * this.game.width
                        ),
                        1000
                    )
                );

                var answers = MONSTER.Common.getAnswersMinusCurrent(
                    this.answers, obj
                );

                this.hit = true;
                this.removeAnswers(answers);

                if (obj.word === this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);

            }
        }
    }
};
