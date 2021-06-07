// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        rows: [],
        pid: 0,
        currently_displayed: 0,
        playlist_loading: true,

        playlist_author_url: "",
        playlist_owner: -20,
        playlist_picture: "",
        playlist_link: "",
        playlist_owner_name: "",
        playlist_name: "",

        add_mode: false,
        add_comment_txt: "",
        comments: [],

        current_user: -10,
        current_user_name: "",
    };

    app.change_post_status = function (post_status){
        app.vue.currently_displayed = post_status;
        axios.post(post_playlist_url,
            {
                pid: app.vue.pid,
                post_status: post_status,
            });
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.complete = (comments) =>{
        comments.map((comment)=>{
            comment.reply_mode = false,
            comment.add_reply_txt = "",
            comment.replies = [];
        })
    }

    app.set_add_status = function (comment_idx, new_status) {
        if (comment_idx === -1){
            app.vue.add_mode = new_status;
        }
        else{ 
            app.vue.comments[comment_idx].reply_mode = new_status;
        }
        
        if (new_status == false) {
            app.reset_form(comment_idx);
        }
    };
    
    app.reset_form = function (comment_idx) {
        if (comment_idx === -1){
            app.vue.add_comment_txt = "";
        }
        else{ 
            app.vue.comments[comment_idx].add_reply_txt = "";
        }
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
                replies : [],
                reply_mode : false,
                add_reply_txt : "",
                comment_author_url: response.data.author_url
            });
            app.enumerate(app.vue.comments);
            app.reset_form(-1);
            app.set_add_status(-1,false);
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

    app.add_reply = function (comment_idx) {
        let replies = app.vue.comments[comment_idx].replies;
        axios.post(add_reply_url,
            {
                comment_id: app.vue.comments[comment_idx].id,
                reply_txt: app.vue.comments[comment_idx].add_reply_txt,
            }).then(function (response) {
            app.vue.current_user_name = response.data.current_user_name;
            replies.push({
                id: response.data.id,
                reply_author: app.vue.current_user,
                reply_txt: app.vue.comments[comment_idx].add_reply_txt,
                author_name: response.data.author,
            });
            app.enumerate(replies);
            app.reset_form(comment_idx);
            app.set_add_status(comment_idx,false);
        });
    };

    app.delete_reply = function (comment_idx, row_idx) {
        let id = app.vue.comments[comment_idx].replies[row_idx].id;
        axios.get(delete_reply_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.comments[comment_idx].replies.length; i++) {
                if (app.vue.comments[comment_idx].replies[i].id === id) {
                    app.vue.comments[comment_idx].replies.splice(i, 1);
                    app.enumerate(app.vue.comments[comment_idx].replies);
                    break;
                }
            }
        });
    };

    app.methods = {
        change_post_status: app.change_post_status,
        set_add_status: app.set_add_status,
        reset_form: app.reset_form,
        add_comment: app.add_comment,
        delete_comment: app.delete_comment,
        add_reply: app.add_reply,
        delete_reply: app.delete_reply,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });



    app.init = () => {
        axios.get(load_playlist_url).then(function(response) {
            let rows = response.data.rows;
            app.vue.rows = rows;
            app.vue.playlist_picture = response.data.playlist_picture;
            app.vue.playlist_link = response.data.playlist_link;
            app.vue.playlist_owner = response.data.playlist_owner;
            app.vue.playlist_owner_name = response.data.playlist_owner_name;
            app.vue.current_user = response.data.current_user;
            app.vue.currently_displayed = response.data.currently_displayed;
            app.vue.pid = response.data.pid;
            app.vue.playlist_name = response.data.playlist_name;
            app.vue.playlist_author_url = response.data.playlist_author_url;
            axios.get(load_comments_url).then(function(response){
                let comments = response.data.comments;
                app.vue.current_user_name = response.data.current_user_name;
                app.complete(comments);
                app.vue.comments = app.enumerate(comments);
            }).then(function(response){
                for (let comment of app.vue.comments) {
                    axios.get(load_replies_url, {params: {"comment_id": comment.id}})
                        .then((response) =>{
                            comment.replies = response.data.replies;
                            comment.replies = app.enumerate(comment.replies);
                        });
                }
                app.vue.playlist_loading = false;
            });
        });
    };


    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);