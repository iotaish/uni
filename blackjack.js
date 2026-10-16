/**
 * blackjack.js - ブラックジャックのゲームロジック
 */

const SUITS = [
    { code: 'S', symbol: '♠', name: 'スペード' },
    { code: 'H', symbol: '♥', name: 'ハート' },
    { code: 'D', symbol: '♦', name: 'ダイヤ' },
    { code: 'C', symbol: '♣', name: 'クラブ' }
];

const RANKS = [
    { num: 1, label: 'A' },
    { num: 2, label: '2' },
    { num: 3, label: '3' },
    { num: 4, label: '4' },
    { num: 5, label: '5' },
    { num: 6, label: '6' },
    { num: 7, label: '7' },
    { num: 8, label: '8' },
    { num: 9, label: '9' },
    { num: 10, label: '10' },
    { num: 11, label: 'J' },
    { num: 12, label: 'Q' },
    { num: 13, label: 'K' }
];

/**
 * 52枚のデッキを生成してシャッフルして返す
 */
function createDeck() {
    const deck = [];
    for (const suit of SUITS) {
        for (const rank of RANKS) {
            deck.push(`${suit.code}_${rank.num}`);
        }
    }
    // Fisher-Yates シャッフル
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
}

/**
 * カード文字列（例: 'S_1'）をオブジェクトに変換
 */
function parseCard(cardStr) {
    if (!cardStr) return null;
    const [suitCode, numStr] = cardStr.split('_');
    const num = parseInt(numStr, 10);
    const suit = SUITS.find(s => s.code === suitCode) || { symbol: '?', name: '?' };
    const rank = RANKS.find(r => r.num === num) || { label: String(num) };

    let value = num;
    if (num > 10) value = 10;
    if (num === 1) value = 11; // 初期値として11

    return {
        id: cardStr,
        suitSymbol: suit.symbol,
        suitName: suit.name,
        suitCode: suitCode,
        rankLabel: rank.label,
        num: num,
        value: value,
        isRed: suitCode === 'H' || suitCode === 'D'
    };
}

/**
 * カードリスト（文字列配列またはカンマ区切り文字列）からカードオブジェクト配列を取得
 */
function parseCards(cards) {
    if (!cards) return [];
    const list = Array.isArray(cards) ? cards : cards.split(',').filter(Boolean);
    return list.map(parseCard);
}

/**
 * 手札の合計点数を計算（Aの11/1自動調整）
 */
function calculateScore(cards) {
    const cardObjs = Array.isArray(cards) && cards.length > 0 && typeof cards[0] === 'object'
        ? cards
        : parseCards(cards);

    let score = 0;
    let aceCount = 0;

    for (const card of cardObjs) {
        if (!card) continue;
        if (card.num === 1) {
            aceCount++;
            score += 11;
        } else if (card.num >= 10) {
            score += 10;
        } else {
            score += card.num;
        }
    }

    // 合計が21を超える場合、Aを11から1へ（-10点）調整
    while (score > 21 && aceCount > 0) {
        score -= 10;
        aceCount--;
    }

    return score;
}

/**
 * 初期手札を配る
 */
function dealInitialCards(deck) {
    const deckCards = Array.isArray(deck) ? [...deck] : deck.split(',').filter(Boolean);
    const player = [deckCards.pop(), deckCards.pop()];
    const dealer = [deckCards.pop(), deckCards.pop()];
    return {
        playerCards: player,
        dealerCards: dealer,
        remainingDeck: deckCards
    };
}

/**
 * カードを1枚引く
 */
function drawCard(deck) {
    const deckCards = Array.isArray(deck) ? [...deck] : deck.split(',').filter(Boolean);
    const card = deckCards.pop();
    return {
        drawnCard: card,
        remainingDeck: deckCards
    };
}

/**
 * ディーラーが17以上になるまでカードを引く処理
 */
function playDealerTurn(dealerCards, deck) {
    const currentDealer = Array.isArray(dealerCards) ? [...dealerCards] : dealerCards.split(',').filter(Boolean);
    let currentDeck = Array.isArray(deck) ? [...deck] : deck.split(',').filter(Boolean);

    while (calculateScore(currentDealer) < 17 && currentDeck.length > 0) {
        const { drawnCard, remainingDeck } = drawCard(currentDeck);
        currentDealer.push(drawnCard);
        currentDeck = remainingDeck;
    }

    return {
        dealerCards: currentDealer,
        remainingDeck: currentDeck
    };
}

/**
 * 勝敗判定
 */
function judgeGame(playerCards, dealerCards) {
    const pScore = calculateScore(playerCards);
    const dScore = calculateScore(dealerCards);
    const pCount = (Array.isArray(playerCards) ? playerCards : playerCards.split(',')).length;
    const dCount = (Array.isArray(dealerCards) ? dealerCards : dealerCards.split(',')).length;

    const pBJ = (pScore === 21 && pCount === 2);
    const dBJ = (dScore === 21 && dCount === 2);

    let result = '';
    let message = '';

    if (pScore > 21) {
        result = 'lose';
        message = 'バーストしました！あなたの負けです。';
    } else if (dScore > 21) {
        result = 'win';
        message = 'ディーラーがバーストしました！あなたの勝ちです！';
    } else if (pBJ && dBJ) {
        result = 'push';
        message = '両者ブラックジャック！引き分け（Push）です。';
    } else if (pBJ) {
        result = 'win';
        message = 'ブラックジャック成立！あなたの勝ちです！';
    } else if (dBJ) {
        result = 'lose';
        message = 'ディーラーがブラックジャックです。あなたの負けです。';
    } else if (pScore > dScore) {
        result = 'win';
        message = `あなたの勝ちです！（${pScore} 対 ${dScore}）`;
    } else if (pScore < dScore) {
        result = 'lose';
        message = `ディーラーの勝ちです。（${pScore} 対 ${dScore}）`;
    } else {
        result = 'push';
        message = `同点（${pScore}点）のため、引き分け（Push）です。`;
    }

    return {
        playerScore: pScore,
        dealerScore: dScore,
        result: result,
        message: message,
        isPlayerBJ: pBJ,
        isDealerBJ: dBJ
    };
}

module.exports = {
    createDeck,
    parseCard,
    parseCards,
    calculateScore,
    dealInitialCards,
    drawCard,
    playDealerTurn,
    judgeGame
};
