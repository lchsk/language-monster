MONSTER.PlaneGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (MONSTER.Key && MONSTER.Key.isUp(MONSTER.Key.UP) && this.ship.position.y > this.ship.height * 1.5)
    {
        if ( ! this.ship.v_up)
        {
            this.ship.v_up = true;

            // this.ship.rotation = 0.3;
        }
    }

    if (this.ship)
    {
        // up

        if (this.ship.v_up)
        {
            this.ship.start_y = this.ship.position.y;
            this.ship.v_time = 0.0;

            var val = t * 0.2;
            this.ship.v_up_tmp += val;
            this.ship.position.y -= val;

            if (this.ship.v_up_tmp >= 40)
            {
                this.ship.v_up_tmp = 0;
                this.ship.v_up = false;
                // this.ship.rotation = 0;
            }

            return;
        }

        // falling down

        var T = 2000.0;

        this.ship.v_time += t;

        var pct = MONSTER.Easing.easeInOutQuart(this.ship.v_time / T);

        this.ship.position.y = Math.round(pct * (this.ship.stop_y - this.ship.start_y)) + this.ship.start_y;

        // this.ship.rotation = 0;

        if (this.ship.v_time > T)
            this.ship.position.y = this.ship.stop_y;


        // make sure the plane fits in the screen

        if (this.ship.position.x > this.game.width - this.ship.width / 2)
            this.ship.position.x = this.game.width - this.ship.width / 2;
        if (this.ship.position.x < this.ship.width / 2)
            this.ship.position.x = this.ship.width / 2;
    }
};

MONSTER.PlaneGame.prototype.checkCollisions = function()
{
    if (this.ship && ! this.hit)
    {
        var left = 0;

        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];

            // if (obj.r.contains(this.ship.position.x, this.ship.position.y))
            if (Math.abs(obj.text.position.x - this.ship.position.x) < this.ship.width / 2 &&
                Math.abs(obj.text.position.y - this.ship.position.y) < this.ship.height / 2
            )
            {
                this.hit = true;
                this.shipActive = false;
                // this.ship.tint = 0x000000;
                this.ship.alpha = 0.5;
                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
            else if (obj.text.position.x < obj.text.width / 2)
            {
                left++;
            }
        }

        if (left == this.answers.length)
        {
            this.constant_answer_speed = true;
            this.hit = true;
            this.shipActive = false;
            this.ship.alpha = 0.5;
            this.moveOutOfScreen();
            MONSTER.Common.negative(this);
        }
    }
};
