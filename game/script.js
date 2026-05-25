const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const livesEl = document.getElementById("lives");
const startMenu = document.getElementById("startMenu");
const startButton = document.getElementById("startButton");

const width = canvas.width;
const height = canvas.height;

const COLORS = {
  darkGray: "#141419",
  playerBlue: "#5da4ff",
  yellow: "#ffdc5a",
  zombieGreen: "#70c23c",
  red: "#ff4d4d",
  white: "#f5f5f5",
  lightGray: "#b4b4b4",
  darkLine: "#1e1e24"
};

let gameState = {
  player: {
    x: width / 2 - 24,
    y: height - 80,
    width: 48,
    height: 48,
    speed: 6,
  },
  bullets: [],
  zombies: [],
  keys: {},
  score: 0,
  lives: 3,
  spawnCooldown: 0,
  gameOver: false,
  started: false,
};

function startGame() {
  gameState.started = true;
  gameState.keys = {};
  startMenu.classList.add("hidden");
}

function drawBackground() {
  ctx.fillStyle = COLORS.darkGray;
  ctx.fillRect(0, 0, width, height);
  
  ctx.strokeStyle = "rgba(40, 40, 50, 0.3)";
  ctx.lineWidth = 1;
  for (let i = 0; i < height; i += 20) {
    ctx.beginPath();
    ctx.moveTo(0, i);
    ctx.lineTo(width, i);
    ctx.stroke();
  }
  
  ctx.fillStyle = "rgba(30, 30, 36, 0.5)";
  ctx.fillRect(0, height - 100, width, 100);
}

function drawPlayer() {
  const p = gameState.player;
  ctx.fillStyle = COLORS.playerBlue;
  ctx.fillRect(p.x, p.y, p.width, p.height, 12);
  ctx.strokeStyle = COLORS.white;
  ctx.lineWidth = 2;
  ctx.strokeRect(p.x + 10, p.y + 10, p.width - 20, p.height - 20);
}

function drawBullets() {
  gameState.bullets.forEach(bullet => {
    ctx.fillStyle = COLORS.yellow;
    ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
    ctx.strokeStyle = COLORS.lightGray;
    ctx.lineWidth = 1;
    ctx.strokeRect(bullet.x, bullet.y, bullet.width, bullet.height);
  });
}

function drawZombies() {
  gameState.zombies.forEach(zombie => {
    ctx.fillStyle = COLORS.zombieGreen;
    ctx.fillRect(zombie.x, zombie.y, zombie.width, zombie.height);
    
    ctx.fillStyle = COLORS.darkLine;
    ctx.beginPath();
    ctx.arc(zombie.x + 10, zombie.y + 14, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(zombie.x + zombie.width - 10, zombie.y + 14, 6, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(zombie.x + 8, zombie.y + 30);
    ctx.lineTo(zombie.x + zombie.width - 8, zombie.y + 30);
    ctx.stroke();
  });
}

function drawUI() {
  ctx.fillStyle = COLORS.white;
  ctx.font = "32px Arial";
  ctx.fillText(`Score: ${gameState.score}`, 20, 50);
  ctx.fillText(`Lives: ${gameState.lives}`, width - 200, 50);
}

function drawGameOver() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
  ctx.fillRect(0, 0, width, height);
  
  ctx.fillStyle = COLORS.red;
  ctx.font = "bold 48px Arial";
  ctx.textAlign = "center";
  ctx.fillText("Game over", width / 2, height / 2 - 60);
  
  ctx.fillStyle = COLORS.white;
  ctx.font = "32px Arial";
  ctx.fillText(`Final score: ${gameState.score}`, width / 2, height / 2 + 20);
  
  ctx.fillStyle = COLORS.lightGray;
  ctx.font = "24px Arial";
  ctx.fillText("Press R to restart or Esc to quit", width / 2, height / 2 + 80);
  
  ctx.textAlign = "left";
}

function updatePlayer() {
  const p = gameState.player;
  let dx = 0;
  if (gameState.keys["ArrowLeft"] || gameState.keys["a"] || gameState.keys["A"]) dx -= 1;
  if (gameState.keys["ArrowRight"] || gameState.keys["d"] || gameState.keys["D"]) dx += 1;
  
  p.x += dx * p.speed;
  p.x = Math.max(0, Math.min(width - p.width, p.x));
}

function updateBullets() {
  gameState.bullets = gameState.bullets.filter(bullet => {
    bullet.y -= bullet.speed;
    return bullet.y + bullet.height > 0;
  });
}

function updateZombies() {
  gameState.zombies.forEach(z => z.y += z.speed);
  
  gameState.zombies = gameState.zombies.filter(zombie => {
    if (zombie.y > height) {
      gameState.lives--;
      return false;
    }
    return true;
  });
  
  gameState.bullets.forEach((bullet, bIdx) => {
    gameState.zombies.forEach((zombie, zIdx) => {
      if (
        bullet.x < zombie.x + zombie.width &&
        bullet.x + bullet.width > zombie.x &&
        bullet.y < zombie.y + zombie.height &&
        bullet.y + bullet.height > zombie.y
      ) {
        gameState.bullets.splice(bIdx, 1);
        gameState.zombies.splice(zIdx, 1);
        gameState.score += 10;
      }
    });
  });
  
  const p = gameState.player;
  gameState.zombies = gameState.zombies.filter(zombie => {
    if (
      p.x < zombie.x + zombie.width &&
      p.x + p.width > zombie.x &&
      p.y < zombie.y + zombie.height &&
      p.y + p.height > zombie.y
    ) {
      gameState.lives--;
      return false;
    }
    return true;
  });
}

function spawnZombie() {
  const size = 42;
  gameState.zombies.push({
    x: Math.random() * (width - size),
    y: -size,
    width: size,
    height: size,
    speed: 1.4 + Math.random() * 1.4,
  });
}

function updateSpawning() {
  gameState.spawnCooldown--;
  if (gameState.spawnCooldown <= 0) {
    spawnZombie();
    gameState.spawnCooldown = Math.max(16, 45 - Math.floor(gameState.score / 30));
  }
}

function update() {
  if (!gameState.started || gameState.gameOver) return;
  
  updatePlayer();
  updateBullets();
  updateZombies();
  updateSpawning();
  
  if (gameState.lives <= 0) {
    gameState.gameOver = true;
  }
}

function draw() {
  drawBackground();
  drawBullets();
  drawZombies();
  drawPlayer();
  drawUI();
  
  if (gameState.gameOver) {
    drawGameOver();
  }
  
  scoreEl.textContent = `Score: ${gameState.score}`;
  livesEl.textContent = `Lives: ${Math.max(0, gameState.lives)}`;
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

function resetGame() {
  gameState = {
    player: {
      x: width / 2 - 24,
      y: height - 80,
      width: 48,
      height: 48,
      speed: 6,
    },
    bullets: [],
    zombies: [],
    keys: {},
    score: 0,
    lives: 3,
    spawnCooldown: 0,
    gameOver: false,
    started: true,
  };
  startMenu.classList.add("hidden");
}

startButton.addEventListener("click", startGame);

window.addEventListener("keydown", event => {
  gameState.keys[event.key] = true;
  
  if (event.key === " " || event.key === "Spacebar") {
    event.preventDefault();
    if (gameState.started && !gameState.gameOver) {
      const p = gameState.player;
      gameState.bullets.push({
        x: p.x + p.width / 2 - 4,
        y: p.y - 18,
        width: 8,
        height: 18,
        speed: 9,
      });
    }
  }
  
  if (event.key === "r" || event.key === "R") {
    if (gameState.gameOver) {
      resetGame();
    }
  }
  
  if (event.key === "Escape") {
    if (gameState.gameOver) {
      location.reload();
    }
  }
});

window.addEventListener("keyup", event => {
  gameState.keys[event.key] = false;
});

loop();
