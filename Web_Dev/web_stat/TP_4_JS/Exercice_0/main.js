const cityColors = {
    "Agadir": "orange",
    "Casablanca": "red",
    "Rabat": "blue",
    "Fes": "green",
    "Marrakech": "purple",
    "default": "transparent",
};

const select_city = document.getElementById("first");
const color_box = document.getElementById("color_box");
const custom_field = document.getElementById('newfield');
const new_city = document.getElementById("new_city");
const color_picker = document.getElementById("color_picker");
const add_city_button = document.getElementById("add_city");

select_city.addEventListener('change',function () {
    const selected_city = this.value;
    if (selected_city === 'autre') {
        custom_field.style.display = 'block';
        color_box.style.backgroundColor = 'transparent';
    } else if (selected_city){
        custom_field.style.display = 'none';
        color_box.style.backgroundColor = cityColors[selected_city];
    } else {
        custom_field.style.display = 'none';
        color_box.style.backgroundColor = 'transparent';
    }
});

color_picker.addEventListener('input', function () {
    const selected_color = this.value;
    color_box.style.backgroundColor = selected_color.toUpperCase();
});

add_city_button.addEventListener('click',function () {
    const city_name = new_city.value.trim();
    const city_color = color_picker.value;

    if (cityn)
});