// 34
function change_color(newColor){
    var elem = document.getElementById('para');
    elem.innerHTML = "Bravo ! ";
    elem.style.color = newColor;
}

var Bout = document.getElementsByTagName('button');
alert('Nb Button : ' + Bout.length);

// 37
var pa = document.getElementsByClassName('cls'); // pa est un tableau
pa[0].style.color = "red";
pa[0].style.fontSize = "25px";
pa[0].style.fontWeight = "bold";
pa[1].innerHTML = "Nouveau premier ";