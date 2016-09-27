MONSTER.ShooterGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (MONSTER.Key && MONSTER.Key.isUp(MONSTER.Key.UP))
    {
        if ( ! this.ship.v_up && ! this.ship.v_down)
        {
            this.ship.textures = this.textures_jump;
            this.ship.v_up = true;
            this.ship.start_y = this.ship.position.y;
            this.ship.stop_y = this.ship.start_y - 200;

        }
    }
    if (MONSTER.Key && MONSTER.Key.isUp(MONSTER.Key.DOWN))
    {
        if ( ! this.ship.v_down && ! this.ship.v_up)
        {
            this.ship.rotation = 3/4 * 2 * MONSTER.Const.PI;
            this.ship.gotoAndStop(1);
            this.ship.v_down = true;
            this.ship.position.y = this.slide_y;
        }
    }

    if (this.ship)
    {

        // slide

        if (this.ship.v_down)
        {
            this.slide_t += t;

            if (this.slide_t > 1200)
            {
                this.slide_t = 0;
                this.ship.v_down = false;
                this.ship.rotation = 0;
                this.ship.play();
                this.ship.position.y = this.original_y;
            }
        }

        // up

        else if (this.ship.v_up)
        {
            var T = 700.0;

            this.ship.v_time += t;

            var pct = MONSTER.Easing.easeOutQuart(this.ship.v_time / T);

            this.ship.position.y =
                Math.round(
                    pct * (this.ship.stop_y - this.ship.start_y))
                + this.ship.start_y;

            if (this.ship.v_time > T)
            {
                this.ship.v_time = 0.0;
                this.ship.v_up = false;
                this.ship.position.y = this.ship.stop_y;
            }
        }

        // falling down

        if ( ! this.ship.v_up && this.ship.position.y < this.original_y)
        {
            this.ship.position.y += t * 0.3;
        }

        if (this.ship.position.y > this.original_y)
        {
            // on the ground
            this.jump_count = 0;
            this.ship.textures = this.textures;
        }


        // make sure the plane fits in the screen

        if (this.ship.position.x > this.game.width - this.ship.width / 2)
            this.ship.position.x = this.game.width - this.ship.width / 2;
        if (this.ship.position.x < this.ship.width / 2)
            this.ship.position.x = this.ship.width / 2;
    }
};

MONSTER.ShooterGame.prototype.checkHit = function()
{
    if (this.ship && ! this.hit)
    {
        // var left = 0;

        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];
            var collision = false;

            if (obj.text.position.x >= this.crosshair.position.x - this.crosshair.width &&
                obj.text.position.x <= this.crosshair.position.x + this.crosshair.width &&
                obj.text.position.y >= this.crosshair.position.y - this.crosshair.height &&
                obj.text.position.y <= this.crosshair.position.y + this.crosshair.height
            )
                collision = true;

            if (collision)
            {
                this.hit = true;
                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
        }
    }
};
