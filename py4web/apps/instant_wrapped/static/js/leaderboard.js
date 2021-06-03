// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        rows: [],
        leaderboard_loading: true,
        current_user: -1,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };


    app.complete = (rows) => {
        // Initializes useful fields of rows.
        rows.map((row) => {
            row.current_score = 0;
            row.upvote_status = 0;
        })
    };

    app.upvote = function (row_idx, new_upvote_status) {
        let row = app.vue.rows[row_idx];
        row.upvote_status = new_upvote_status;
        if (new_upvote_status === 1){
            row.current_score += 1;
        }
        else {
            row.current_score -=1;
        }
        axios.post(upvote_url, {
            playlist_id: row.id,
            upvote_status: row.upvote_status,
            new_score: row.current_score,
        }).then(function (response) {
            let rows = app.vue.rows;
            rows.sort(function(a, b) {
                return b.current_score - a.current_score;
            });
            Vue.set(app.vue.rows, app.enumerate(rows));
            });
    };

    app.save_playlist= function (PID) {
        axios.post(save_playlist_url, {
            pid: PID,
        });
    };

    app.methods = {
        upvote: app.upvote,
        save_playlist: app.save_playlist,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });



    app.init = () => {
        axios.get(load_leaderboard_url).then(function (response) {
            app.vue.current_user = response.data.current_user;
            let rows = response.data.rows;
            app.complete(rows);
            app.vue.rows = app.enumerate(rows);
            })
            .then(() => {
                for (let row of app.vue.rows) {
                    axios.get(get_rating_url, {params: {"playlist_id": row.id}})
                        .then((response) => {
                            row.upvote_status = response.data.upvote_status;
                            row.current_score = response.data.current_score;
                            app.vue.leaderboard_loading = false;
                        });
                }
            });
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);