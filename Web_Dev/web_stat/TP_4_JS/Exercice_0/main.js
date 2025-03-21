var cityColors = {
    "Agadir": "orange",
    "Casablanca": "red",
    "Rabat": "blue",
    "Fes": "green",
    "Marrakech": "purple",
    "default": "transparent",
};

var select_city = document.getElementById("first");
var color_box = document.getElementById("color_box");
var custom_field = document.getElementById('newfield');
var new_city = document.getElementById("new_city");
var color_picker = document.getElementById("color_picker");
var add_city_button = document.getElementById("add_city");

select_city.addEventListener('change',function () {
    var selected_city = this.value;
    if (selected_city === 'autre') {
        custom_field.style.display = 'block';
        color_box.style.backgroundColor = 'transparent';
    } else if (selected_city){
        custom_field.style.display = 'block';
        color_box.style.backgroundColor = cityColors[selected_city];
    } else {
        custom_field.style.display = 'none';
        color_box.style.backgroundColor = 'transparent';
    }
});

color_picker.addEventListener('input', function () {
    var selected_color = this.value;
    color_box.style.backgroundColor = selected_color.toUpperCase();
});

add_city_button.addEventListener('click',function () {
    var city_name = new_city.value.trim();
    var city_color = color_picker.value;

    if (city_name && city_color){
        var option = document.createElement('option');
        option.value = city_name;
        option.textContent = city_name;
        select_city.insertBefore(option,select_city.lastElementChild);
        cityColors[city_name] = city_color;

        new_city.value = '';
        color_picker.value = '#000000';
        custom_field.style.display = 'none';

        select_city.value = city_name;
        color_box.style.backgroundColor = city_color;
    } else {
        alert('Veuillez saisir une ville et une couleur');
    }
});



var a_color_box = document.getElementById("color_box_A");
a_color_box.style.backgroundColor = 'transparent';
a_color_box.style.width = 200 + 'px';
a_color_box.style.height = 100 + 'px';
a_color_box.style.margin = 10 + 'px';
a_color_box.style.border = '2px solid black';
a_color_box.style.float = 'left';


const color_box1 = document.getElementById("color_box1");
color_box1.addEventListener('mouseover',function() {
    a_color_box.style.backgroundColor = color_box1.style.backgroundColor;
});
color_box1.addEventListener('mouseout',function() {
    a_color_box.style.backgroundColor = 'transparent';
});
const color_box2 = document.getElementById("color_box2");
color_box2.addEventListener('mouseover',function() {
    a_color_box.style.backgroundColor = color_box2.style.backgroundColor;
});
color_box2.addEventListener('mouseout',function() {
    a_color_box.style.backgroundColor = 'transparent';
});
const color_box3 = document.getElementById("color_box3");
color_box3.addEventListener('mouseover',function() {
    a_color_box.style.backgroundColor = color_box3.style.backgroundColor;
});
color_box3.addEventListener('mouseout',function() {
    a_color_box.style.backgroundColor = 'transparent';
});
const color_box4 = document.getElementById("color_box4");
color_box4.addEventListener('mouseover',function() {
    a_color_box.style.backgroundColor = color_box4.style.backgroundColor;
});
color_box4.addEventListener('mouseout',function() {
    a_color_box.style.backgroundColor = 'transparent';
});
const color_box5 = document.getElementById("color_box5");
color_box5.addEventListener('mouseover',function() {
    a_color_box.style.backgroundColor = color_box5.style.backgroundColor;
});
color_box5.addEventListener('mouseout',function() {
    a_color_box.style.backgroundColor = 'transparent';
});

const text_area = document.getElementById("text_area");
const b_box = document.getElementById("box_B");
const c_box = document.getElementById("box_C");
const copy_box = document.getElementById("copy");
const cut_box = document.getElementById("cut");
const double_click_box = document.getElementById("double_click");

text_area.addEventListener('copy', function(){
    var text = text_area.value;
    let count = text.split(" ").length;
    b_box.textContent = text.replaceAll(' ','') + " Ce texte contient " + count + " mots";
    b_box.style.color = 'blue';
});
copy_box.addEventListener('click', function(){
    var text = text_area.value;
    let count = text.split(" ").length;
    b_box.textContent = text.replaceAll(' ','') + " Ce texte contient " + count + " mots";
    b_box.style.color = 'blue';
});
text_area.addEventListener("cut",function () {
    var text = text_area.value;
    let count = text.split(" ").length;
    c_box.textContent = text.replaceAll(" ","") + " Ce texte contient " + count + " mots";
    c_box.style.color = 'white';
});
cut_box.addEventListener('click', function(){
    var text = text_area.value;
    let count = text.split(" ").length;
    c_box.textContent = text.replaceAll(' ','') + " Ce texte contient " + count + " mots";
    c_box.style.color = 'white';
});

double_click_box.addEventListener('click',function (){
    if (confirm('Are you sure?')){
        text_area.value = '';
        b_box.textContent = '';
        c_box.textContent = '';
    }
});

