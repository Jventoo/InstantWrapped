// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        rows: [],
    };


    app.methods = {

    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });



    app.init = () => {
        axios.get(load_playlist_url).then(function (response) {
            let rows = response.data.rows;
            app.vue.rows = rows;
            })
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);