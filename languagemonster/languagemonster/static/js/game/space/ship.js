MONSTER.SpaceGame.prototype.createShip = function(textures) {
    var animation = new PIXI.extras.MovieClip(textures);

    animation.animationSpeed = 0.5;
    animation.anchor.x = animation.anchor.y = 0.5;
    animation.position.x = -1000;

    return animation;
};

MONSTER.SpaceGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.LEFT)) {
        this.ship.rotation -= t * this.rotation_v;

        this.turn(MONSTER.Const.LEFT);
    }
    else if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.RIGHT)) {
        this.ship.rotation += t * this.rotation_v;

        this.turn(MONSTER.Const.RIGHT);
    } else {
        this.turn(MONSTER.Const.AHEAD);
    }

    if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.UP))
        this.ship_v += t * this.acceleration + (1 / (this.max_v * this.max_v));
    else if (MONSTER.Key && MONSTER.Key.isDown(MONSTER.Key.DOWN))
        this.ship_v -= t * this.brakes;

    if (this.ship)
    {
        var x = this.ship.position.x;
        var y = this.ship.position.y;
        var angle = this.ship.rotation;
        var new_x = x * Math.cos (angle) - y * Math.sin (angle);
        var new_y = x * Math.sin (angle) + y * Math.cos (angle);

        this.ship.position.x += this.ship_v * Math.cos(angle - MONSTER.Const.PI_2);
        this.ship.position.y += this.ship_v * Math.sin(angle - MONSTER.Const.PI_2);

        // drag
        this.ship_v -= this.drag * t;

        if (this.ship_v < this.min_v)
            this.ship_v = this.min_v;
        if (this.ship_v > this.max_v)
            this.ship_v = this.max_v;

        if (this.ship.position.x > this.game.width)
            this.ship.position.x = this.game.width - this.ship.position.x;
        else if (this.ship.position.x < 0)
            this.ship.position.x = this.game.width - this.ship.position.x;
        if (this.ship.position.y > this.game.height)
            this.ship.position.y = this.game.height - this.ship.position.y;
        else if (this.ship.position.y < 0)
            this.ship.position.y = this.game.height - this.ship.position.y;
    }
};

MONSTER.SpaceGame.prototype.turn = function(direction) {
    var main = null;
    var other = [];

    if (direction === MONSTER.Const.LEFT) {
        main = this.ship_left;

        other.push(this.ship_normal);
        other.push(this.ship_right);
    } else if (direction === MONSTER.Const.RIGHT) {
        main = this.ship_right;

        other.push(this.ship_normal);
        other.push(this.ship_left);
    } else {
        main = this.ship_normal;

        other.push(this.ship_right);
        other.push(this.ship_left);
    }

    main.position.x = this.ship.position.x;
    main.position.y = this.ship.position.y;
    main.rotation = this.ship.rotation;

    main.play();

    for (var i = 0; i < 2; i++) {
        other[i].stop();
        other[i].position.x = -1000;
    }

    this.ship = main;
};

MONSTER.SpaceGame.prototype.checkCollisions = function()
{
    if (this.ship && this.ship_v > 0 && ! this.hit)
    {
        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];

            if (obj.r.contains(this.ship.position.x, this.ship.position.y))
            {
                this.hit = true;

                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else {
                    this.shipActive = false;

                    this.ship_normal.alpha
                        = this.ship_left.alpha
                        = this.ship_right.alpha = 0.5;

                    MONSTER.Common.negative(this);
                }
            }
        }
    }
};
