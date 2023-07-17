/* base_internal.js */

$(function(){
    // make_breadcrumbs([]);
});

/* パンくずリストを作る */
function make_breadcrumbs(pages_list){
    let bc_elm = $("#breadcrumbs");
    bc_elm.empty();

    let ol = $("<ol />");
    for(let i=0; i<pages_list.length; i++){
        let name = pages_list[i][0];
        let url = pages_list[i][1];

        let a = $("<a />")
            .attr("href", url)
            .text(name)
        ;

        let li = $("<li />")
            .append(a);
        
        ol.append(li);
    }
    bc_elm.append(ol);
}

