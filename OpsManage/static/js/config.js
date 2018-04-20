$(function () {
 pageTog(0,250);
});
function pageTog(num1,num2) {
            var pageTog=document.querySelector("#page-tog");
            pageTog.onclick=function(){
                var sidebar=$(".sidebar");
                var pageWrapper=$("#page-wrapper");
                if(sidebar.width()==num1){
                    sidebar.animate({
                        width:num2+'px',
                    });
                     sidebar.find('.sidebar-nav').css({
                         visibility:'inherit'
                     });
                    $(this).animate({
                        left:(num2-10)+'px'
                    });
                    pageWrapper.animate({
                        marginLeft:num2+'px'
                    })
                }else{
                    sidebar.animate({
                        width:num1
                    });
                     sidebar.find('.sidebar-nav').css({
                         visibility:'hidden'
                     });
                     $(this).animate({
                        left:num1
                    });
                    pageWrapper.animate({
                        marginLeft:num1
                 })
            }
        };
    }