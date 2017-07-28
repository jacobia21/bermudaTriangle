var profileID = '';
var userLoggedIn = false;

$(document).ready(function() {
  $('.like-button').click(setColor);
  $('.sidebarbtn').click(function() {
    $('.sidebar').toggleClass('active');
  });
});
function setColor(e){
  if (!userLoggedIn) return alert("You must be logged in to like a post.");
  var img = $(e.currentTarget).find("img");
  var imageStr = $(img).attr("src").split("/");
  imageStr = imageStr[imageStr.length-1];
  var empty = "emptypaw.png";
  var full = "filledpaw.png";
  var startUrl = "../resources/"

  var key = $("span").has(e.currentTarget).find("em").html();

  if (imageStr==empty) {
    $(img).attr("src",startUrl+full);
    $('#postLike').val(key);
    var form = $('form').has('#postLike');
    form.find(".uidInput").val(profileID);
    form.find(".submitForm").click();
  }
  else {
    $(img).attr("src",startUrl+empty);
    $('#postUnlike').val(key);
    var form = $('form').has("#postUnlike");
    form.find(".uidInput").val(profileID);
    form.find(".submitForm").click();
  }
}
