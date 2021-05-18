// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        time_range: -1,
        desired_data: "",
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
        app.vue.counter = 1;
        app.vue.time_range = new_range;
        let time_range = app.vue.time_range;
        axios.get(load_stats_url, {params: {time_range: new_range}}).then(function (response) {
            app.vue.rows = response.data.rows;
        });
    }

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