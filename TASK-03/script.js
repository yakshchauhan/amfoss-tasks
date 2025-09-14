const successSound = document.getElementById("successSound");
const failSound = document.getElementById("failSound");
const drawSound = document.getElementById("drawSound");
const welcomeSound = document.getElementById("welcomeSound");
const bgMusic = document.getElementById("bgMusic"); 
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const SCORE = document.getElementById("score");
const BESTSCORE = document.getElementById("bestScore");

// ---------------------------Narration parts-------------------------
const part1 = document.getElementById("part1");
const part2 = document.getElementById("part2");
const part3 = document.getElementById("part3");
const part4 = document.getElementById("part4");
const narrationOverlay = document.getElementById("loading_screen_overlay");

let drawing = false;
let points = [];
let gameLocked = true;    // to make the game lock until narration ends

// ------------------------Loading best score-----------------------------
let bestScore = sessionStorage.getItem("bestScore") || 0;
BESTSCORE.textContent = `🏆 Best Score: ${bestScore}%`;

// -----------------------narration starts on first click------------------
window.addEventListener("click", function() {
    if (part1.paused) {
        part1.play();
    }
}, { once: true });

// ------------------- narration------------------------------------ 
part1.addEventListener("ended", () => part2.play());
part2.addEventListener("ended", () => part3.play());
part3.addEventListener("ended", () => part4.play());   

// ----------Hide overlay, unlock game, and start background music after last narration----------------
part4.addEventListener("ended", () => {
  narrationOverlay.classList.add("hide");
  gameLocked = false;
  document.getElementById("scoreboard").style.display = "block"; 
  bgMusic.play(); 
});


// --------------------------Drawing logic-----------------------------------
canvas.addEventListener("mousedown", () => {
  if (gameLocked) return;
  drawing = true;
  points = [];
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  drawSound.play();
});

canvas.addEventListener("mousemove", (event) => {
  if (!drawing || gameLocked) return;

  const x = event.offsetX;
  const y = event.offsetY;

  points.push({ x, y });

  ctx.lineTo(x, y);
  ctx.strokeStyle = "white";
  ctx.lineWidth = 2;
  ctx.stroke();
});

canvas.addEventListener("mouseup", () => {
  if (gameLocked) return;
  drawing = false;
  drawSound.pause();
  drawSound.currentTime = 0;
  checkCircle();
});

// ------------------Circle accuracy check-----------------------------
function checkCircle() {
  if (points.length < 22) {
    failSound.play();
    SCORE.textContent = " 💀 Lost to kindergarden geometry!";                 
    return;
  }  

  // ---------------------Find center------------------------------------
  let sumX = 0, sumY = 0;
  for (let i = 0; i < points.length; i++) {
    sumX = sumX + points[i].x;
    sumY = sumY + points[i].y;
  }
  const avgX = sumX / points.length;
  const avgY = sumY / points.length;

  // -------------------Distances from center-------------------------------
  const distances = [];
  for (const p of points) {
    const dx = p.x - avgX;
    const dy = p.y - avgY;
    distances.push(Math.hypot(dx, dy));
  }

  // -----------------Average distance (radius)--------------------------------
  let sum = 0;
  for (let i = 0; i < distances.length; i++) {
    sum = sum + distances[i];
  }
  let avgDist = sum / distances.length;

  // ------------------Standard deviation-----------------------------------------
  function standardDeviation(values, mean) {
    let sum = 0;
    for (const v of values) {
      const diff = v - mean;
      sum = sum + (diff * diff);
    }
    return Math.sqrt(sum / values.length);
  }
  const stdDev = standardDeviation(distances, avgDist);

  // ------------------- Normalize accuracy-----------------------------
  let accuracy = (1 - stdDev / avgDist) * 100;
  if (accuracy < 0) accuracy = 0;
  if (accuracy > 100) accuracy = 100;

  // --------------------- Shape check----------------------------------
  if (accuracy < 69) {
    SCORE.textContent = "Try again… Picasso 🎨";
    failSound.play();
    return;
  }

  // -------------------------- Show score-------------------------------
  let roundedAccuracy = Math.round(accuracy);
  SCORE.textContent = "⭕ Circle Accuracy: " + roundedAccuracy + "%";
  if (accuracy >= 69) {
    successSound.play();
  } 
  else {
  failSound.play();
  }

  // ---------------------Update best score--------------------------------
  if (accuracy > bestScore) {
    let roundedAccuracy = Math.round(accuracy)
    bestScore = roundedAccuracy
    sessionStorage.setItem("bestScore", bestScore);
    BESTSCORE.textContent = "🏆 Best Score:" + bestScore + "%";
  }
}
