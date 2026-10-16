const express = require("express");
const path = require('path');
const { getOmikuji, getComment } = require('./omikuji');
const {
  createDeck,
  parseCards,
  calculateScore,
  dealInitialCards,
  drawCard,
  playDealerTurn,
  judgeGame
} = require('./blackjack');

const app = express();

app.set('view engine', 'ejs');
app.use("/public", express.static(path.join(__dirname + "/public")));
app.use(express.urlencoded({ extended: true }));

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
  res.render('blackjack');
});

app.get("/blackjack/game", (req, res) => {
  let playerCards, dealerCards, deck;

  if (!req.query.p || !req.query.d || !req.query.deck) {
    // 新規ゲーム開始: デッキ作成 & 初期手札配布
    const newDeck = createDeck();
    const dealt = dealInitialCards(newDeck);
    playerCards = dealt.playerCards;
    dealerCards = dealt.dealerCards;
    deck = dealt.remainingDeck;
  } else {
    playerCards = req.query.p.split(',').filter(Boolean);
    dealerCards = req.query.d.split(',').filter(Boolean);
    deck = req.query.deck.split(',').filter(Boolean);

    if (req.query.action === 'hit') {
      const { drawnCard, remainingDeck } = drawCard(deck);
      if (drawnCard) {
        playerCards.push(drawnCard);
        deck = remainingDeck;
      }
    }
  }

  const pScore = calculateScore(playerCards);
  const isBust = pScore > 21;

  res.render('game', {
    playerCards: parseCards(playerCards),
    dealerCards: parseCards(dealerCards),
    playerScore: pScore,
    isBust: isBust,
    pStr: playerCards.join(','),
    dStr: dealerCards.join(','),
    deckStr: deck.join(',')
  });
});

app.get("/blackjack/rlt", (req, res) => {
  const playerCards = (req.query.p || '').split(',').filter(Boolean);
  let dealerCards = (req.query.d || '').split(',').filter(Boolean);
  let deck = (req.query.deck || '').split(',').filter(Boolean);

  // プレイヤーがバーストしていない場合、ディーラーは17以上になるまでカードを引く
  if (calculateScore(playerCards) <= 21) {
    const dealerTurn = playDealerTurn(dealerCards, deck);
    dealerCards = dealerTurn.dealerCards;
    deck = dealerTurn.remainingDeck;
  }

  const outcome = judgeGame(playerCards, dealerCards);

  res.render('result', {
    playerCards: parseCards(playerCards),
    dealerCards: parseCards(dealerCards),
    outcome: outcome
  });
});

app.listen(8080, () => console.log("Example app listening on port 8080!"));
