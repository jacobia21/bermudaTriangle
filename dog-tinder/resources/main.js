$(document).ready(function() {
  $('.like-button').click(setColor);
  $('.sidebarbtn').click(function() {
    $('.sidebar').toggleClass('active');
  });
});
function setColor(e){
  $(e.currentTarget).toggleClass('liked');
}
