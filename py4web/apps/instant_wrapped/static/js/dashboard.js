// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        stats_loaded: false,
        stats_loading: false,
        time_range: -1,
        save_mode: false,
        playlist_saved: false,
        playlist_to_post: false,
        pid: 0,
        add_playlist_name: "",
        desired_data: "Top Songs",
        top_tracks: [],
        rows: [],
        counter: 0,
    };

    // app.enumerate = (a) => {
    //     // This adds an _idx field to each element of the array.
    //     let k = 0;
    //     a.map((e) => {e._idx = k++;});
    //     return a;
    // };

    // app.set_time_range = function () {
    //
    // };

    app.load_stats = function (new_range) {
        app.vue.stats_loaded = false;
        app.vue.stats_loading = true;
        app.vue.save_mode = false;
        app.vue.playlist_saved = false;
        app.vue.playlist_to_post = false;
        app.vue.pid = "";
        app.vue.counter = 1;
        app.vue.time_range = new_range;
        app.reset_form();
        let time_range = app.vue.time_range;
        axios.get(load_stats_url, {params: {time_range: new_range}}).then(function (response) {
            app.vue.rows = response.data.rows;
            app.vue.top_tracks = response.data.top_tracks;
            app.vue.stats_loaded = true;
            app.vue.stats_loading = false;
        });
    };

    app.reset_form = function () {
        app.vue.add_playlist_name = "";
    };

    app.set_save_status = function (new_status) {
        app.vue.save_mode = new_status;
        if (new_status == false) {
            app.reset_form();
        }
    };

    app.create_playlist = function (playlist_tracks) {
        axios.post(create_playlist_url,
            {
                top_tracks: playlist_tracks,
                name: app.vue.add_playlist_name,
            }).then(function (response) {
                app.vue.pid = response.data.pid;
                app.reset_form();
                app.set_save_status(false);
                app.vue.playlist_to_post = true;
                app.vue.playlist_saved = true;
         });
    };

    app.post_playlist = function (playlist_id) {
        axios.post(post_playlist_url,
            {
                pid: playlist_id,
                post_status: true,
            });
            app.set_save_status(false);
            app.vue.playlist_to_post = false;
    };

    // app.increment = function () {
    //     app.vue.counter += 1;
    // }

    // app.display_stats = function () {
    //     if (app.vue.desired_data === "Top Artists"){
    //
    //     }
    //     let range = app.vue.range;
    //     axios.get(load_stats_url, {params: {range: new_range}}).then(function (response) {
    //     });
    // }

    app.methods = {
        load_stats: app.load_stats,
        reset_form: app.reset_form,
        set_save_status: app.set_save_status,
        create_playlist: app.create_playlist,
        post_playlist: app.post_playlist,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });


    app.init = () => {
        app.vue.counter =1;
        app.vue.time_range = -1;
    };

    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);