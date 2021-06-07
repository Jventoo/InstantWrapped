// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        profile_loading: true,
        stats_loading: false,

        following: false,
        num_followers: 0,
        num_following: 0,
        followers_url: "",

        current_user: -1,
        current_user_name: "",

        user_id: -1,
        user_name: "",
        user_picture: "",
        biography: "",

        top_songs: [],
        top_artists: [],
        top_genres: [],
        top_playlists: [],

        add_mode: false,
        add_comment_txt: "",
        comments: [],
    };

    app.set_following = function(new_status) {
        if (new_status) {
            axios.post(start_follow_url, {params: {user_id: app.vue.user_id}}).then(function (response) {
                app.vue.num_followers++;
                app.vue.following = true;
            });
        } else {
            axios.post(stop_follow_url, {params: {user_id: app.vue.user_id}}).then(function (response) {
                app.vue.num_followers--;
                app.vue.following = false;
            });
        }
    }

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
        if (new_status == false) {
            app.reset_form();
        }
    };
    
    app.reset_form = function () {
        app.vue.add_comment_txt = "";
    };


    app.add_comment = function () {
        axios.post(add_comment_url,
            {
                comment_txt: app.vue.add_comment_txt,
            }).then(function (response) {
                app.vue.current_user_name = response.data.current_user_name;
                app.vue.comments.push({
                    id: response.data.id,
                    comment_author: app.vue.current_user,
                    comment_txt: app.vue.add_comment_txt,
                    author_name: response.data.author,
                });
                app.enumerate(app.vue.comments);
                app.reset_form();
                app.set_add_status(false);
        });
    };


    app.delete_comment = function (row_idx) {
        let id = app.vue.comments[row_idx].id;
        axios.get(delete_comment_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.comments.length; i++) {
                if (app.vue.comments[i].id === id) {
                    app.vue.comments.splice(i, 1);
                    app.enumerate(app.vue.comments);
                    break;
                }
            }
        });
    };

    app.methods = {
        set_following: app.set_following,
        set_add_status: app.set_add_status,
        reset_form: app.reset_form,
        add_comment: app.add_comment,
        delete_comment: app.delete_comment,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });


    app.init = () => {
        axios.get(load_profile_url).then(function (response) {
            app.vue.user_name = response.data.user_name;
            app.vue.user_picture = response.data.user_picture;
            app.vue.biography = response.data.biography;
            app.vue.user_id = response.data.user_id;
            app.vue.current_user = response.data.current_user;

            app.vue.top_songs = response.data.top_songs;
            app.vue.top_artists = response.data.top_artists;
            app.vue.top_genres = response.data.top_genres;
            app.vue.top_playlists = response.data.playlists;

            app.vue.following = response.data.following;
            app.vue.num_followers = response.data.num_followers;
            app.vue.num_following = response.data.num_following;
            app.vue.followers_url = response.data.followers_url;

            app.vue.profile_loading = false;

            axios.get(load_comments_url).then(function(response){
                let comments = response.data.comments;
                app.vue.current_user_name = response.data.current_user_name;
                app.vue.comments = app.enumerate(comments);
            });

            if (app.vue.top_songs.length == 0 || app.vue.top_artists.length == 0 ||  app.vue.top_genres.length == 0 )
            {
                app.vue.stats_loading = true;
                axios.get(load_stats_url, {params: {time_range: 2}}).then(function (response) {
                    app.vue.rows = response.data.rows;
                    axios.get(load_profile_url).then(function (new_response) {
                        app.vue.top_songs = new_response.data.top_songs;
                        app.vue.top_artists = new_response.data.top_artists;
                        app.vue.top_genres = new_response.data.top_genres;
                        app.vue.stats_loading = false;
                    });
                });
            }
        });
    };

    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);