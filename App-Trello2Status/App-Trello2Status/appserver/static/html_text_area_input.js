require(["jquery",
        "splunkjs/mvc",
        "splunkjs/mvc/simplexml/ready!"],
    function($, mvc) {
    var defaultTokenModel = mvc.Components.get("default");
    var submitTokenModel = mvc.Components.get("submitted");
    $(document).on("change","#html_ta_user_comment",function(){
        var strComment=$(this).val();
        var strTokComment=defaultTokenModel.get("tokComment");
        if(strComment!=="" && strComment!==undefined){
            if(strTokComment!==undefined || strTokComment!==strComment){
                defaultTokenModel.set("tokComment",strComment);
                submitTokenModel.set("tokComment",strComment);
            }
        }else{
            defaultTokenModel.unset("tokComment");
            submitTokenModel.unset("tokComment");
        }
    });
});
