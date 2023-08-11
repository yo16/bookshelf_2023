
$(function(){
    /* toggle-button */
    $(".btn_toggle").on("click", function() {
        $(".btn_toggle").toggleClass("checked");
        if(!$('input[name="check"]').prop("checked")) {
            $(".btn_toggle input").prop("checked", true);
        } else {
            $(".btn_toggle input").prop("checked", false);
        }
    });
});
