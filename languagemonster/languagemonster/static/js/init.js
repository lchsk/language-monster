$('.btn-popover').popover({placement: 'auto'});

new Vue({
    delimiters: ["[[", "]]"],
    el: '#monster-home',
    data: {
        view: 'main',
        base_lang: null,
        target_lang: null,
        target_lang_name: null,
        lang_pair: null,
        datasets: null,
        vis_datasets: null,
        selected_flag: null,
        datasets_offset: 0,
        datasets_pp: 4,
        datasets_cp: 0, // current page
        datasets_btns: [false, false], // show prev/next buttons in datasets
        datasets_pages: 0,
        langs_to_learn: null
    },
    created: function () {
        this.load_menu_data();
    },
    methods: {
        load_game: function(){
            this.show_play_now = false;
            this.view = 'languages';
        },
        select_language: function(language) {
            this.target_lang_name = language.target_language.original_name;
            this.target_lang = language.target_language.acronym;
            this.lang_pair = this.base_lang + '_' + this.target_lang;
            this.selected_flag
                = language.target_language.flag_filename.replace('24', '30');

            this.view = 'datasets';

            this.filter_datasets();
        },
        filter_datasets: function() {
            var sets = [];

            for (var i = 0; i < this.datasets.length; i++) {
                if (this.lang_pair === this.datasets[i].lang_pair) {
                    sets.push(this.datasets[i]);
                }
            }

            this.datasets_cp
                = Math.floor(this.datasets_offset / this.datasets_pp) + 1;
            this.datasets_pages = Math.floor(sets.length / this.datasets_pp) + 1;

            this.datasets_btns
                = [this.datasets_cp > 1, this.datasets_cp < this.datasets_pages];

            this.vis_datasets = sets.slice(
                this.datasets_offset,
                this.datasets_offset + this.datasets_pp
            );
        },
        prev_sets_page: function() {
            this.datasets_offset -= this.datasets_pp;
            this.filter_datasets();
        },
        next_sets_page: function() {
            this.datasets_offset += this.datasets_pp;
            this.filter_datasets();
        },
        load_script: function(script_scr) {
            var self = this;

            var script = document.createElement('script');

            script.type = 'text/javascript';
            script.async = true;
            script.src = script_scr;
            script.addEventListener('load', function () {
                self.init_game();
            }, false);

            var tag = document.getElementsByTagName('script')[0];

            tag.parentNode.insertBefore(script, tag);
        },
        goto: function(view) {
            this.view = view;
        },
        init_game: function() {
            if (window.PIXI && window.MONSTER) {
                MONSTER.newGame();
            }
        },
        play: function(dataset_id) {
            this.view = 'game';

            this.load_script('/static/lib/pixi.js');
            this.load_script('/static/js_build/games.js');

            window.play = true;
            // TODO:
            // window.games = window.games;
            window.games_played = window.games;
            window.canvas_only = false;
            // TODO:
            window.debug = window.debug;
            window.data = {
                dataset_id: dataset_id
            };
            // TODO:
            window.translations = window.translations;
        },
        load_menu_data: function () {
            var self = this;

            $.ajax({
                method: 'GET',
                timeout: 15000,
                url: '/api/local/to-study/' + window.language,
                success: function(resp) {
                    if (resp['status'] === 'success') {
                        self.datasets = resp['data']['datasets'];
                        var langs = resp['data']['langs_to_learn'];

                        for (var i = 0; i < langs.length; i++)
                            langs[i].target_language.flag_filename += '_24px';

                        if (langs.length > 0)
                            self.base_lang = langs[0].base_language.acronym;

                        self.langs_to_learn = langs;
                    }
                },
                // TODO:
                error: function(x, t) {

                }
            });
        }
    }
});
