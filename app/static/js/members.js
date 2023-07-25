/* members.js */

$(function(){
    $("#comment_angle_down").click(function(){
        let div_comment = $("#comments");
        if (div_comment.css("display") == "none"){
            // 非表示→表示
            div_comment.slideDown('fast');
            
            // 上向き→下向き(transformしない)
            $(this).attr("transform", "")
        }else{
            // 表示→非表示
            div_comment.slideUp('fast');

            // 下向き→上向き(transformでy軸反転)
            $(this).attr("transform", "scale(1,-1)")
        }
        return false;
    });

    $("#his_angle_down").click(function(){
        let div_comment = $("#borrowed_his");
        if (div_comment.css("display") == "none"){
            // 非表示→表示
            div_comment.slideDown('fast');
            
            // 上向き→下向き(transformしない)
            $(this).attr("transform", "")
        }else{
            // 表示→非表示
            div_comment.slideUp('fast');

            // 下向き→上向き(transformでy軸反転)
            $(this).attr("transform", "scale(1,-1)")
        }
        return false;
    });
});
