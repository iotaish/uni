/**
 * blackjack.js - サーバー側デッキ・乱数ドロー管理モジュール
 */

const SUITS = ['S', 'H', 'D', 'C'];
const RANKS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];

// 進行中のゲーム状態をインメモリで保持
const games = new Map();

/**
 * 52枚のデッキを生成してシャッフル（乱数）
 */
function createShuffledDeck() {
    const deck = [];
    for (const suit of SUITS) {
        for (const rank of RANKS) {
            deck.push(`${suit}_${rank}`);
        }
    }
    // Fisher-Yates シャッフル (Math.random)
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
}

/**
 * カードの数値を計算（ディーラーの17以上判定用）
 */
function calculateDealerScore(cards) {
    let score = 0;
    let aceCount = 0;
    for (const c of cards) {
        const num = parseInt(c.split('_')[1], 10);
        if (num === 1) {
            aceCount++;
            score += 11;
        } else if (num >= 10) {
            score += 10;
        } else {
            score += num;
        }
    }
    while (score > 21 && aceCount > 0) {
        score -= 10;
        aceCount--;
    }
    return score;
}

/**
 * 新規ゲームの開始 (POST /api/blackjack/start)
 */
function startNewGame() {
    const deck = createShuffledDeck();
    const player = [deck.pop(), deck.pop()];
    const dealerVisible = deck.pop();
    const dealerHidden = deck.pop();

    const gameId = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    games.set(gameId, {
        deck,
        dealerCards: [dealerVisible, dealerHidden],
        createdAt: Date.now()
    });

    // 1時間以上古いゲームセッションを掃除
    const oneHourAgo = Date.now() - 3600000;
    for (const [id, data] of games.entries()) {
        if (data.createdAt < oneHourAgo) games.delete(id);
    }

    return {
        gameId,
        player,
        dealerVisible
    };
}

/**
 * カードを1枚引く (POST /api/blackjack/hit)
 */
function drawCard(gameId) {
    const game = games.get(gameId);
    if (!game || game.deck.length === 0) {
        return null;
    }
    const card = game.deck.pop();
    return {
        card,
        remaining: game.deck.length
    };
}

/**
 * ディーラーのターン完了 (POST /api/blackjack/stand)
 */
function finishDealerTurn(gameId) {
    const game = games.get(gameId);
    if (!game) return null;

    const dealerCards = [...game.dealerCards];
    while (calculateDealerScore(dealerCards) < 17 && game.deck.length > 0) {
        dealerCards.push(game.deck.pop());
    }

    games.delete(gameId); // ゲーム終了時に削除
    return {
        dealerCards
    };
}

export {
    startNewGame,
    drawCard,
    finishDealerTurn
};
