const layer = document.getElementById("layer");
const startButton = document.getElementById("startButton");

let dx = 3; 
let dy = 0; 
let animationId;
let goingDown = true; 

function startAnimation() {
  const color = document.getElementById("colorInput").value;
  const width = parseInt(document.getElementById("widthInput").value) || 150;
  const height = parseInt(document.getElementById("heightInput").value) || 100;
  const text = document.getElementById("textInput").value || "Calque";
  const opacity = parseFloat(document.getElementById("opacityInput").value) || 1;

  layer.style.backgroundColor = color;
  layer.style.width = width + "px";
  layer.style.height = height + "px";
  layer.style.opacity = opacity;
  layer.textContent = text;

  layer.style.left = "0px";
  layer.style.top = "150px";

  dx = Math.abs(dx); 
  dy = 0; 
  goingDown = true;

  cancelAnimationFrame(animationId);
  moveLayer();
}

function moveLayer() {
  const rect = layer.getBoundingClientRect();
  let x = rect.left;
  let y = rect.top;
  const w = rect.width;
  const h = rect.height;

  const winW = window.innerWidth;
  const winH = window.innerHeight;

  x += dx;
  y += dy;

  if (dx > 0 && x + w >= winW) { 
    dx = -dx; 
    y += goingDown ? h : -h; 
  } else if (dx < 0 && x <= 0) {
    dx = -dx; 
    y += goingDown ? h : -h; 
  }

  if (goingDown && y + h >= winH) {
    goingDown = false;
    y = winH - h; 
  } 
  else if (!goingDown && y <= 0) {
    goingDown = true; 
    y = 0; 
  }

  layer.style.left = x + "px";
  layer.style.top = y + "px";

  animationId = requestAnimationFrame(moveLayer);
}

window.addEventListener("resize", () => {
  if (animationId) {
    cancelAnimationFrame(animationId);
    moveLayer();
  }
});

startButton.addEventListener("click", startAnimation);