/* maintenance.js */

$(function(){
    $("#search_book").click(function(){
        let isbn = $("#isbn").val();
        console.log("isbn:" + isbn);
        get_book(isbn);
    });
    $("#btn_add_genre").click(function(){
        // 今の入力状態
        let cur_genres_str = $("#genres").val();
        let cur_genres = [];
        if (cur_genres_str.length > 0){
            cur_genres = cur_genres_str.split(",");
        }
        // 今選択されているgenre
        let added_genre = $("#sel_genre").val();
        // 入力されている場合は、何もせず抜ける
        if (cur_genres.includes(added_genre)){
            return;
        }
        // 入力されていない場合は、追加する
        cur_genres.push(added_genre);
        // 入力
        $("#genres").val(cur_genres.join(","))
    });

    initialize();

    // for debug
    $("#isbn").val(9784768705261);
})

function get_book(isbn){
    ret = {};
    if (isbn == "") {
        console.log("search_book_by_isbn() needs isbn code.")
        return;
    }

    // ハイフンが入っていたら除く
    isbn = isbn.replace(/\-/g, "");
    $("#isbn").val(isbn);

    // isbnコードをチェックする
    $("#spnSearchISBNMessage").empty();
    if (!validate_isbn_code(isbn)) {
        console.log('illigal ISBN code.');
        $("#spnSearchISBNMessage")
            .append($("<br></br>"))
            .append($("<span></span>")
                .addClass("warning_message")
                .text("ISBNコードが不正です。")
            );
        return;
    }
    
    dispLoading("検索中...");

    initialize();
    $("#isbn").val(isbn);

    // 本を検索 using Ajax
    $.ajax({
        url: "./get_book_with_isbn",
        type: "POST",
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            "isbn": isbn
        })
    })
    .done((data) => {
        js_data = JSON.parse(data.ResultSet);
        console.log(js_data);
        
        $("#isbn").val(isbn);
        $("#book_name").val(js_data["book_name"]);
        $("#num_of_authors").val(js_data["authors"].length);
        for(var i=0; i<js_data["authors"].length; i++ ){
            $("#author"+i).val(js_data["authors"][i]["author_name"]);
        }
        $("#publisher_code").val(js_data["publisher_code"]);
        $("#publisher_name").val(js_data["publisher_name"]);
        if (js_data["image_url"].length > 0){
            $("#img_thumbnail").attr("src", js_data["image_url"])
            $("#spnImageThumbnail").css("display", "");
            $("#image_url").val(js_data["image_url"]);
        }
        $("#comment").val(js_data["comment"]);
        $("#genres").val(js_data["genres"]);
    })
    .fail((data)=>{
        console.log("Could not found book info by isbn["+isbn+"].");
        console.log(data);

        initialize();
        $("#isbn").val(isbn);
    })
    .always((data)=>{
        removeLoading();
    });
}


/*
initialize
*/
function initialize(){
    $("#isbn").val("");
    $("#book_name").val("");
    $("#author0").val("");
    $("#publisher_name").val("");
    $("#genres").val("");
};

/*
validate_isbn_code();

Returns:
    true: OK
    false: NG
 */
function validate_isbn_code(isbn){
    if ((isbn.length != 10) && (isbn.length != 13)){
        return false;
    }

    var ary_char = isbn.split("");

    // ISBN-10
    if (isbn.length==10) {
        var tmp = (ary_char[0]-0)*10 + (ary_char[1]-0)*9 + (ary_char[2]-0)*8
            + (ary_char[3]-0)*7 + (ary_char[4]-0)*6 + (ary_char[5]-0)*5
            + (ary_char[6]-0)*4 + (ary_char[7]-0)*3 + (ary_char[8]-0)*2;
        var check_num = 11 - tmp % 11;
        if (check_num==10){
            check_num = 'X';
        }else if (check_num==11){
            check_num = '0';
        }
        if (ary_char[9]!=check_num){
            console.log('check digit is ' + check_num);
            return false;
        }
    }else 
    // ISBN-13
    if (isbn.length==13) {
        var tmp = (ary_char[0]-0)*1
            + (ary_char[1]-0)*3
            + (ary_char[2]-0)*1
            + (ary_char[3]-0)*3
            + (ary_char[4]-0)*1
            + (ary_char[5]-0)*3
            + (ary_char[6]-0)*1
            + (ary_char[7]-0)*3
            + (ary_char[8]-0)*1
            + (ary_char[9]-0)*3
            + (ary_char[10]-0)*1
            + (ary_char[11]-0)*3;
        var check_num = (10 - tmp % 10) % 10;
        if (ary_char[12] != check_num){
            console.log('check digit is ' + check_num);
            return false;
        }
    }

    return true;
}

// 参考
// https://webllica.com/jquery-now-loading/
/* ------------------------------
 Loading イメージ表示関数
 引数： msg 画面に表示する文言
 ------------------------------ */
 function dispLoading(msg){
    // 引数なし（メッセージなし）を許容
    if( msg == undefined ){
        msg = "";
    }
    // 画面表示メッセージ
    var dispMsg = "<div class='loadingMsg'>" + msg + "</div>";
    // ローディング画像が表示されていない場合のみ出力
    if($("#loading").length == 0){
        $("body").append("<div id='loading'>" + dispMsg + "</div>");
    }
}

/* ------------------------------
 Loading イメージ削除関数
 ------------------------------ */
function removeLoading(){
    $("#loading").remove();
}

