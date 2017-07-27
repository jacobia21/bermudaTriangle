$(document).ready(function() {
  $('.sidebarbtn').click(function() {
    $('.sidebar').toggleClass('active');
  });
});

function setColor(btn, color){
    var count=1;
    var property = document.getElementsByClassName('button');
    if (count == 0){
        property.style.backgroundColor = "#FFFFFF"
        count=1;
    }
    else{
        property.style.backgroundColor = "#f55d3e"
        count=0;
    }

}
