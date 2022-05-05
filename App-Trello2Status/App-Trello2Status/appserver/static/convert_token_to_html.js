require([
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/simplexml/ready!'
], function($, mvc,) {
    var submittedTokens = mvc.Components.get('submitted');
    // Listen for a change to the token tokHTML value
    submittedTokens.on("change:tokHTML", function(model, tokHTML, options) {
        var tokHTMLJS=submittedTokens.get("tokHTML");
        if (tokHTMLJS!==undefined)
        {
            $("#htmlPanelWithToken").html(tokHTMLJS);
        }
    });
});
