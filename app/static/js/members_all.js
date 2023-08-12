/* members_all.js */

$(function(){
    // tdをクリック時
    $("#tbl_members td").click(function(){
        // tr要素にmember_idが設定されているので取得
        let member_id = $(this).parent().attr("member_id");
        if( member_id ){
            window.location.href = member_page_url + member_id;
        }
    });
});

