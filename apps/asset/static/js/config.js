
$(document).ready(function () {
    pageTog(0,250)
    /*$(".auto-select .selectpicker").each(function (index,obj) {
      selectSize(obj)
    });
    function selectSize(op){
        var text=$(op).next().find('.dropdown-toggle span').text();
         　var strlen = 0;
        　　　　for(var i = 0;i <text.length; i++)
        　　　　{
        　　　　　　if(text.charCodeAt(i) > 255) //如果是汉字，则字符串长度加2
        　　　　　　　　strlen +=3;
        　　　　　　else
        　　　　　　　　strlen++;
        　　　　}
          var text_length =strlen;
         var current_width = parseInt(text_length) *8;
         $(op).next().find('.dropdown-toggle').css("width",current_width+"px");
    }
    $(".auto-select .selectpicker").on('changed.bs.select',function () {
      selectSize(this)
    });*/



});
var pageTog=function(num1,num2){
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
