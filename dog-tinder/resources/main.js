$(document).ready(function() {
  $('.like-button').click(setColor);
  $('.sidebarbtn').click(function() {
    $('.sidebar').toggleClass('active');
  });
});
function setColor(e){
  var img = $(e.currentTarget).find("img");
  var imageStr = $(img).attr("src").split("/");
  imageStr = imageStr[imageStr.length-1];
  var empty = "emptypaw.png";
  var full = "filledpaw.png";
  var startUrl = "../resources/"

  if (imageStr==empty) {
    $(img).attr("src",startUrl+full);
    //window.location = "/likepost?uid="+"&";
  }
  else {
    $(img).attr("src",startUrl+empty);
    //window.location = "/unlikepost"
  }
}
