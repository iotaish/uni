const express = require("express");
const path = require('path');
const { getOmikuji, getComment } = require('./omikuji');
const { startNewGame, drawCard, finishDealerTurn } = require('./blackjack');
const { startWordleGame, evaluateGuess } = require('./wordle');

const app = express();

app.set('view engine', 'ejs');
app.use("/public", express.static(path.join(__dirname + "/public")));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", (req, res) => {
  res.sendFile("index.html", { root: path.join(__dirname, "public") });
});

app.get("/hello1", (req, res) => {
  const message1 = "Hello world";
  const message2 = "Bon jour";
  res.render('show', { greet1: message1, greet2: message2 });
});

app.get("/hello2", (req, res) => {
  res.render('show', { greet1: "Hello world", greet2: "Bon jour" });
});

app.get("/icon", (req, res) => {
  res.render('icon', { filename: "./public/Apple_logo_black.svg", alt: "Apple Logo" });
});

app.get("/omikuji1", (req, res) => {
  const luck = getOmikuji();
  res.send('あなたの運勢は' + luck + 'です');
});

app.get("/omikuji2", (req, res) => {
  const luck = getOmikuji();
  res.render('omikuji2', { result: luck });
});

app.get("/omikuji3", (req, res) => {
  const luck = getOmikuji();
  const comment = getComment(luck);
  res.render('omikuji3', { result: luck, comment: comment });
});

app.get("/english", (req, res) => {
  res.render('greeting', { message: 'Good Morning\n' });
});

app.get("/french", (req, res) => {
  res.render('greeting', { message: 'Bonjour\n' });
});

app.get("/german", (req, res) => {
  res.render('greeting', { message: 'Guten Morgen\n' });
});

// Blackjack ルート
app.get("/blackjack", (req, res) => {
  res.sendFile("blackjack.html", { root: path.join(__dirname, "public") });
});

// Blackjack POST API（乱数・山札ドロー管理）
app.post("/api/blackjack/start", (req, res) => {
  res.json(startNewGame());
});

app.post("/api/blackjack/hit", (req, res) => {
  const result = drawCard(req.body.gameId);
  if (!result) {
    return res.status(400).json({ error: "Game not found or deck empty" });
  }
  res.json(result);
});

app.post("/api/blackjack/stand", (req, res) => {
  const result = finishDealerTurn(req.body.gameId);
  if (!result) {
    return res.status(400).json({ error: "Game not found" });
  }
  res.json(result);
});

// Wordle ルート
app.get("/wordle", (req, res) => {
  res.sendFile("wordle.html", { root: path.join(__dirname, "public") });
});

// Wordle POST API（乱数単語選定・辞書判定）
app.post("/api/wordle/start", (req, res) => {
  res.json(startWordleGame());
});

app.post("/api/wordle/guess", (req, res) => {
  const result = evaluateGuess(req.body.gameId, req.body.guess);
  if (result.error) {
    return res.status(400).json(result);
  }
  res.json(result);
});

app.listen(8080, () => console.log("Example app listening on port 8080!"));
