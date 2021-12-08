var LenNavItems = document.querySelectorAll(".nav-link").length;

for (var i = 0; i < LenNavItems; i++) {

  document.querySelectorAll(".nav-link")[i].addEventListener("click", function() {

    var buttonInnerHTML = this.innerHTML;


    buttonAnimation(buttonInnerHTML);

  });

}



function buttonAnimation(currentKey) {

  var activeButton = document.querySelector("." + currentKey);

  activeButton.classList.add("pressed");

  setTimeout(function() {
    activeButton.classList.remove("pressed");
  }, 100);

}