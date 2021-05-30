// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        rows: [],
        playlist_owner: -20,
        current_user: -10,
        currently_displayed: false,
        pid: 0,

        add_mode: false,
        add_comment_txt: "",
        current_user_email: "",
        current_user_name: "",
        comments: [],
    };

    app.change_post_status = function (post_status){
        app.vue.currently_displayed = post_status;
        console.log(post_status);
        axios.post(post_playlist_url,
            {
                pid: app.vue.pid,
                current_status: post_status,
            });
    };

    app.add_comment = function () {
        axios.post(add_comment_url,
            {
                post_content: app.vue.add_comment_txt,
            }).then(function (response) {
            app.vue.current_user_name = response.data.current_user_name;
            app.vue.current_user_email = response.data.current_user_email;
            app.vue.rows.push({
                id: response.data.id,
                post_content: app.vue.add_comment_txt,
                post_author: response.data.author,
                user_email: response.data.current_user_email,
            });
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
        });
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };
    
    app.reset_form = function () {
        app.vue.add_comment_txt = "";
    };


    app.methods = {
        change_post_status: app.change_post_status,
        add_comment: app.add_comment,
        set_add_status: app.set_add_status,
        reset_form: app.reset_form,
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
            app.vue.playlist_owner = response.data.playlist_owner;
            app.vue.current_user = response.data.current_user;
            app.vue.currently_displayed = response.data.currently_displayed;
            app.vue.pid = response.data.pid;
            })
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);