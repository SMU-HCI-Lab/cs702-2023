let start = -1;
let trajectory = [];

function setup() {
  let canvas = createCanvas(300, 300);
  canvas.parent('canvas-container');
}

function draw() {
  background(230);
  frameRate(12);

  if (mouseIsPressed && mouseX < 300 && mouseY < 300) {
    background(240);

    if (start < 0) {
      start = +Date.now();
    }
    let timestamp = +Date.now() - start;

    trajectory.push([mouseX, mouseY, timestamp])

    strokeWeight(3)
    trajectory.forEach(p => { point(p[0], p[1])})

    point(mouseX, mouseY)
  } else {
    background(230);
    start = -1;

    if (trajectory.length > 0) {
      const data = { 'trajectory': trajectory }
      console.log(data);
      const output = document.getElementById('output');
      output.innerHTML = JSON.stringify(data);
    }

    trajectory = []
  }

  text("X: " + mouseX, 0, 12);
  text("Y: " + mouseY, 0, 24);

}