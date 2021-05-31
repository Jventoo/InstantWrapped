// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_name: "",
        top_songs: [],
        top_artists: [],
        top_genres: [],
        top_playlists: [],
        user_picture: "",
        biography: "",
    };

    app.methods = {
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });


    app.init = () => {
        axios.get(load_profile_url).then(function (response) {
            app.vue.user_name = response.data.user_name;
            app.vue.top_songs = response.data.top_songs;
            app.vue.top_artists = response.data.top_artists;
            app.vue.top_genres = response.data.top_genres;
            app.vue.top_playlists = response.data.playlists;
            app.vue.user_picture = response.data.user_picture;
            app.vue.biography = response.data.biography;
        })
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);