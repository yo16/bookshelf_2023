/* maintenance.js */

$(function(){
    // ISBNフィールド
    $("#isbn").keypress(function(e){
        if (e.keyCode == 13){
            // パンくずリストを空にする
            initialize_breadcrumbs();

            // 検索
            let isbn = $("#isbn").val();
            search_book(isbn);
            
            return false;
        }
    });

    // 本検索ボタン
    $("#btn_search_book").click(function(){
        // パンくずリストを空にする
        initialize_breadcrumbs();

        // 検索
        let isbn = $("#isbn").val();
        search_book(isbn);
            
        return false;
    });

    // ジャンル選択ボタン
    // 選択しているジャンルを登録する
    $("#btn_select_genre").click(function(){
        add_genre(
            $("#sel_genre_master").children(":selected").val(),
            $("#sel_genre_master").children(":selected").text()
        );
        return false;
    });
    // ジャンル除外ボタン
    $("#btn_remove_genre").click(function(){
        remove_genre();
        return false;
    });
    // ジャンルの初期登録
    initialize_genres();

    // 登録ボタン
    $("#btn_regist_book").click(function(){
        // submit
        $("#frm_regist_book").submit();
    });

    // 最初からISBNが入っている場合は、検索する
    if ($("#isbn").val().length > 0) {
        search_book($("#isbn").val());
    }
});

// ISBNから本情報を検索して設定
function search_book(isbn_input){
    //console.log(isbn_input);
    let book_info = {};

    // ハイフンが入っていたら除く
    isbn = isbn_input.replace(/\-/g, "");
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
        
        book_info["isbn"] = isbn;
        book_info["book_name"] = js_data["book_name"];
        book_info["authors"] = [];
        for(let i=0; i<js_data["authors"].length; i++ ){
            book_info["authors"].push(
                js_data["authors"][i]["author_name"]
            );
        }
        book_info["publisher_code"] = js_data["publisher_code"];
        book_info["publisher_name"] = js_data["publisher_name"];
        book_info["image_url"] = "";
        if ("image_url" in js_data) {
            book_info["image_url"] = js_data["image_url"];
        }
        book_info["published_dt"] = js_data["published_dt"];
        book_info["original_description"] = js_data["original_description"];
        book_info["description"] = js_data["description"];
        book_info["page_count"] = js_data["page_count"];
        book_info["dimensions_height"] = js_data["dimensions_height"];
        book_info["dimensions_width"] = js_data["dimensions_width"];
        book_info["dimensions_thickness"] = js_data["dimensions_thickness"];
        book_info["genres"] = [];
        for(let i=0; i<js_data["genres"].length; i++){
            book_info["genres"].push(js_data["genres"][i]);
        }
        book_info["added_dt"] = js_data["added_dt"];
        book_info["num_of_same_books"] = js_data["num_of_same_books"];

        // できたbook_infoを使って画面を更新
        set_book_info(book_info);
    })
    .fail((data)=>{
        console.log("Could not found book info by isbn["+isbn+"].");
        console.log(data);
    })
    .always((data)=>{
        removeLoading();
    });

    return;
}

// 本情報から、画面項目へ設定
function set_book_info(book_info){
    //console.log({book_info});

    // book_infoの登録
    let val_pattern_items = [
        "book_name",
        "image_url",
        "description_original",
        "description",
        "publisher_code",
        "publisher_name",
        "published_dt",
        "page_count",
        "dimensions_height",
        "dimensions_width",
        "dimensions_thickness",
        "added_dt",
        "num_of_same_books"
    ];
    for(let i=0; i<val_pattern_items.length; i++){
        let item = val_pattern_items[i];
        $("#"+item).val(book_info[item]);
    }
    $("#image_url_img").attr("src", book_info["image_url"]);
    $("#spn_authors").empty();
    for(let i=0; i<book_info["authors"].length; i++){
        // textareaに追加
        let cur = $("#authors").val()
        cur += book_info["authors"][i] + "\n";
        $("#authors").val(cur);

        // inputを追加
        let ent = $("<input>")
            .attr("id", "author_show"+i)
            .attr("name", "author_show"+i)
            .attr("class", "author_show")
            .attr("readonly", "1")
            .val(book_info["authors"][i])
        ;
        $("#spn_authors").append(ent);
    }
    $("genres").empty();
    for(let i=0; i<book_info["genres"].length; i++){
        let genre_id = book_info["genres"][i]["genre_id"];
        let genre_name = book_info["genres"][i]["genre_name"];
        add_genre(genre_id, genre_name);
    }

    // 登録日
    $("#added_dt").val()
}

function initialize_breadcrumbs(){
    // パンくずリストの再作成
    // まだ作ってないとき用に空にする
    make_breadcrumbs(
        [["本の追加","{{ url_for('maintenance') }}"]]
    )
}

// ジャンルを追加する
function add_genre(genre_id, genre_name){
    // 指定されたgenre_idがすでに登録済の場合、何もせず終了する
    let found_same_val = false;
    $("#sel_genre_selected option").each(function(){
        if (genre_id == $(this).val()) {
            found_same_val = true;
        }
    });
    if (found_same_val){
        return false;
    }

    // スペーサーが入ってたら除去
    genre_name = genre_name.replace(/　/g, "");

    // まだ追加されていないので追加する
    let new_opt = $("<option></option>")
        .val(genre_id)
        .text(genre_name);
    $("#sel_genre_selected").append(new_opt);

    // #genres(hidden form項目)にも追加する
    $("#genres").val($("#genres").val()+genre_id+",");

    return true;
}

// 選択しているジャンルを除外する
function remove_genre(){
    // 選択しているジャンル
    // （HTMLで１行選択しかできないことにしているが
    //   複数選択でも正常に動く）
    let cur_genres = $("#sel_genre_selected option:selected");
    if (cur_genres.length == 0){
        return false;
    }
    // 除外
    cur_genres.remove();

    // genre_idを取得
    let ids = [];
    cur_genres.each(function(){
        ids.push($(this).attr("value"));
    });
    // idを#genresから探して削除する
    genres_text = $("#genres").val();
    genres_text = genres_text.replace(/,+$/,"");    // 末尾の,を削除
    gernes_text_ary = genres_text.split(",");
    genres_text_ary_removed = gernes_text_ary.filter(function(v){
        return !ids.includes(v);
    });
    $("#genres").val(genres_text_ary_removed.join(",")+",")

    // もし全部除外して空になってしまったら、
    // #sel_genre_masterのval=0の要素（分類なしのはず）を
    // 追加する
    let exists_genres = $("#sel_genre_selected option");
    if (exists_genres.length == 0){
        initialize_genres();
    }

    return true;
}

// val=0のジャンル（分類なし）だけを追加
function initialize_genres(){
    let genres = $("#sel_genre_selected");

    // val=0のジャンル名を取得
    // （"分類なし"のはずだが、念のため取得）
    let val0_text = "分類なし";
    $("#sel_genre_master option").each(function(){
        if ($(this).val() == 0){
            val0_text = $(this).text();
            return;
        }
    });

    // 強制的に全部空にする
    genres.empty();
    // val0を追加
    let val0 = $("<option></option>")
        .val(0)
        .text(val0_text);
    genres.append(val0);
    // テキストは0を入れる
    $("#genres").val("0,");
    
    return;
}


/*
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

    //initialize();

    // for debug
    //$("#isbn").val(9784768705261);
})
*/
/*
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
        $("#published_dt").val(js_data["published_dt"]);
        $("#original_description").val(js_data["original_description"]);
        $("#description").val(js_data["description"]);
        $("#page_count").val(js_data["page_count"]);
        $("#dimensions_height").val(js_data["dimensions_height"]);
        $("#dimensions_width").val(js_data["dimensions_width"]);
        $("#dimensions_thickness").val(js_data["dimensions_thickness"]);
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

*/


/*
initialize
*/
function initialize(){
    //$("#isbn").val("");
    $("#book_name").val("");
    $("#author0").val("");
    $("#publisher_name").val("");
    $("#genres").val("");
    $("#sel_genre_selected").empty();
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

