MONSTER.DataLoader = function(dataset_id, email, max_rounds, success_func, sender)
{
    this.dataset_id = dataset_id;
    this.email = email;
    this.max_rounds = max_rounds;
    this.pack = {};
    this.success = false;
    this.success_func = success_func;
    this.sender = sender;
};

MONSTER.DataLoader.prototype.constructor = MONSTER.DataLoader;

// Basic way to load stuff
// Words in base and target languages (pairs)
MONSTER.DataLoader.prototype.loadWordPairs = function()
{
    var that = this;
    that.success = false;
    that.error_code = null;

    $.ajax({
        method: "GET",
        crossDomain: false,
        timeout: 15000,
        url: "/api/local/words/" + this.dataset_id + "/" + this.email,
        error: function(x, t) {
            that.success = false;
            that.error_code = t;

            var error_text = MONSTER.Common.trans(
                "Server error, please try again",
                window.translations
            ) + " (" + t + ")";
            that.sender.top_bar_loading_text.text = error_text;
            var new_x = (
                0.5 * that.sender.game.width - 0.5
                * that.sender.top_bar_loading_text.width
            );
            that.sender.top_bar_loading_text.position.x = new_x;

            var b1 = MONSTER.Common.createButton(
                that.sender,
                MONSTER.Common.trans(
                    "Try again",
                    window.translations
                ),
                0,
                0,
                200,
                50,
                300,
                360,
                function() {
                    location.href = window.location.href;
                }
            );
            b1.interactive = true;
            that.sender.game.view.addChild(b1);
        },
        success: function(m) {
            that.word_sets = m;
            that.success = true;

            that.success_func.apply(that.sender, [that.sender]);
        }
    });
};
