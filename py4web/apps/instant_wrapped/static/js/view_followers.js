// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        followers: [],
        following: [],
        profile_url: "",
        user_id: -1,
        username: "",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.methods = {
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        axios.get(load_followers_url, {params: {user_id: app.vue.user_id}}).then(function (response) {
            app.vue.followers = response.data.followers;
            app.vue.following = response.data.following;
            app.vue.profile_url = response.data.profile_url;
            app.vue.user_id = response.data.user_id;
            app.vue.username = response.data.username;
        });     
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);