/**
 * /public/blackjack.js
 * クライアントサイド（ブラウザ）で動作するブラックジャックの演算・進行エンジン
 */

// --- 1. カードおよびデッキのデータ定義とモデル ---
const SUIT_DEFINITIONS = [
    { code: 'S', symbol: '♠', name: 'スペード', isRed: false },
    { code: 'H', symbol: '♥', name: 'ハート', isRed: true },
    { code: 'D', symbol: '♦', name: 'ダイヤ', isRed: true },
    { code: 'C', symbol: '♣', name: 'クラブ', isRed: false }
];

const RANK_DEFINITIONS = [
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

class Card {
    constructor(suitCode, num) {
        this.suitCode = suitCode;
        this.num = num;
        const suit = SUIT_DEFINITIONS.find(s => s.code === suitCode) || { symbol: '?', isRed: false };
        const rank = RANK_DEFINITIONS.find(r => r.num === num) || { label: String(num) };
        this.symbol = suit.symbol;
        this.label = rank.label;
        this.isRed = suit.isRed;
    }

    get id() {
        return `${this.suitCode}_${this.num}`;
    }

    static fromId(id) {
        if (!id) return null;
        const [suitCode, numStr] = id.split('_');
        return new Card(suitCode, parseInt(numStr, 10));
    }
}

class Deck {
    constructor(cards = null) {
        if (cards) {
            this.cards = cards.map(c => (c instanceof Card ? c : Card.fromId(c)));
        } else {
            this.cards = [];
            this.reset();
        }
    }

    reset() {
        this.cards = [];
        for (const suit of SUIT_DEFINITIONS) {
            for (const rank of RANK_DEFINITIONS) {
                this.cards.push(new Card(suit.code, rank.num));
            }
        }
        this.shuffle();
    }

    // Fisher-Yates シャッフル（クライアント側で実行）
    shuffle() {
        for (let i = this.cards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
        }
    }

    draw() {
        return this.cards.pop() || null;
    }

    toIds() {
        return this.cards.map(c => c.id);
    }
}

// --- 2. ゲームルール・演算エンジン (クライアント側で実行) ---
class BlackjackEngine {
    /**
     * 手札の合計スコアを計算（Aの11/1自動切替）
     */
    static calculateScore(cards) {
        let score = 0;
        let aceCount = 0;

        for (const card of cards) {
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

        while (score > 21 && aceCount > 0) {
            score -= 10;
            aceCount--;
        }

        return score;
    }

    /**
     * ディーラーのAI思考演算（17以上になるまで引く）
     */
    static playDealerTurn(dealerCards, deck) {
        while (this.calculateScore(dealerCards) < 17 && deck.cards.length > 0) {
            const card = deck.draw();
            if (card) dealerCards.push(card);
        }
        return dealerCards;
    }

    /**
     * 勝敗判定
     */
    static judge(playerCards, dealerCards) {
        const pScore = this.calculateScore(playerCards);
        const dScore = this.calculateScore(dealerCards);
        const pBJ = (pScore === 21 && playerCards.length === 2);
        const dBJ = (dScore === 21 && dealerCards.length === 2);

        let outcome = 'lose';
        let message = '';

        if (pScore > 21) {
            outcome = 'lose';
            message = 'バーストしました！あなたの負けです。';
        } else if (dScore > 21) {
            outcome = 'win';
            message = 'ディーラーがバーストしました！あなたの勝ちです！';
        } else if (pBJ && dBJ) {
            outcome = 'push';
            message = '両者ブラックジャック！引き分け（Push）です。';
        } else if (pBJ) {
            outcome = 'win';
            message = 'ブラックジャック！あなたの勝ちです！';
        } else if (dBJ) {
            outcome = 'lose';
            message = 'ディーラーがブラックジャックです。あなたの負けです。';
        } else if (pScore > dScore) {
            outcome = 'win';
            message = `あなたの勝ちです！（${pScore} 対 ${dScore}）`;
        } else if (pScore < dScore) {
            outcome = 'lose';
            message = `ディーラーの勝ちです。（${pScore} 対 ${dScore}）`;
        } else {
            outcome = 'push';
            message = `同点（${pScore}点）のため、引き分け（Push）です。`;
        }

        return {
            playerScore: pScore,
            dealerScore: dScore,
            outcome: outcome,
            message: message
        };
    }
}

// --- 3. クライアント側UIレンダラー（<template> を利用） ---
class CardRenderer {
    constructor(templateSelector) {
        this.template = document.querySelector(templateSelector);
    }

    createCardElement(card, isHidden = false) {
        if (!this.template) {
            const li = document.createElement('li');
            li.dataset.state = isHidden ? 'hidden' : 'visible';
            if (card && card.isRed && !isHidden) li.dataset.color = 'red';
            li.textContent = isHidden ? '?' : `${card.symbol} ${card.label}`;
            return li;
        }

        const clone = this.template.content.cloneNode(true);
        const item = clone.querySelector('li') || clone.firstElementChild;

        if (isHidden) {
            item.dataset.state = 'hidden';
            item.textContent = '?';
        } else {
            item.dataset.state = 'visible';
            if (card.isRed) item.dataset.color = 'red';
            item.textContent = `${card.symbol} ${card.label}`;
        }
        return item;
    }

    renderHand(container, cards, hideSecond = false) {
        container.replaceChildren();
        cards.forEach((card, index) => {
            const isHidden = (hideSecond && index >= 1);
            const el = this.createCardElement(card, isHidden);
            container.appendChild(el);
        });
    }
}

// --- 4. ゲーム画面コントローラー (/blackjack/game 用) ---
class GamePageController {
    constructor() {
        this.renderer = new CardRenderer('.card-template');
        this.playerHandList = document.querySelector('[data-role="player-hand"]');
        this.dealerHandList = document.querySelector('[data-role="dealer-hand"]');
        this.playerScoreOutput = document.querySelector('[data-role="player-score"]');
        this.dealerScoreOutput = document.querySelector('[data-role="dealer-score"]');
        this.hitButton = document.querySelector('[data-action="hit"]');
        this.standButton = document.querySelector('[data-action="stand"]');
        this.statusSection = document.querySelector('[data-role="game-status"]');

        this.deck = new Deck();
        this.playerCards = [];
        this.dealerCards = [];

        this.init();
    }

    init() {
        // 新規ゲーム開始: 初期手札を2枚ずつ配る（クライアント側で演算）
        this.playerCards = [this.deck.draw(), this.deck.draw()];
        this.dealerCards = [this.deck.draw(), this.deck.draw()];

        this.saveState();
        this.bindEvents();
        this.updateView();
    }

    bindEvents() {
        if (this.hitButton) {
            this.hitButton.addEventListener('click', () => this.onHit());
        }
        if (this.standButton) {
            this.standButton.addEventListener('click', () => this.onStand());
        }
    }

    // クライアント側でカードを引き、スコアを再計算
    onHit() {
        const drawn = this.deck.draw();
        if (drawn) {
            this.playerCards.push(drawn);
        }
        this.saveState();
        this.updateView();

        const score = BlackjackEngine.calculateScore(this.playerCards);
        if (score > 21) {
            // バースト判定
            if (this.statusSection) {
                this.statusSection.dataset.state = 'bust';
            }
            if (this.hitButton) this.hitButton.disabled = true;
        }
    }

    // クライアント側で状態を保存し、結果画面へ遷移
    onStand() {
        this.saveState();
        window.location.href = '/blackjack/rlt';
    }

    saveState() {
        const state = {
            player: this.playerCards.map(c => c.id),
            dealer: this.dealerCards.map(c => c.id),
            deck: this.deck.toIds()
        };
        sessionStorage.setItem('bj_state', JSON.stringify(state));
    }

    updateView() {
        // プレイヤー手札描画
        this.renderer.renderHand(this.playerHandList, this.playerCards, false);
        const pScore = BlackjackEngine.calculateScore(this.playerCards);
        if (this.playerScoreOutput) {
            this.playerScoreOutput.textContent = `${pScore} 点`;
        }

        // ディーラー手札描画（2枚目は伏せる）
        this.renderer.renderHand(this.dealerHandList, this.dealerCards, true);
        if (this.dealerScoreOutput && this.dealerCards.length > 0) {
            const visibleScore = this.dealerCards[0].num === 1 ? 11 : Math.min(this.dealerCards[0].num, 10);
            this.dealerScoreOutput.textContent = `${visibleScore} 点 + ?`;
        }
    }
}

// --- 5. 結果画面コントローラー (/blackjack/rlt 用) ---
class ResultPageController {
    constructor() {
        this.renderer = new CardRenderer('.card-template');
        this.playerHandList = document.querySelector('[data-role="player-hand"]');
        this.dealerHandList = document.querySelector('[data-role="dealer-hand"]');
        this.playerScoreOutput = document.querySelector('[data-role="player-score"]');
        this.dealerScoreOutput = document.querySelector('[data-role="dealer-score"]');
        this.resultBanner = document.querySelector('[data-role="result-banner"]');
        this.messageOutput = document.querySelector('[data-role="result-message"]');

        this.init();
    }

    init() {
        const rawState = sessionStorage.getItem('bj_state');
        if (!rawState) {
            // 状態がない場合は新規スタートへリダイレクト
            window.location.href = '/blackjack';
            return;
        }

        const state = JSON.parse(rawState);
        const playerCards = state.player.map(id => Card.fromId(id));
        let dealerCards = state.dealer.map(id => Card.fromId(id));
        const deck = new Deck(state.deck);

        // クライアント側でディーラーの思考演算（17以上までドロー）
        const pScore = BlackjackEngine.calculateScore(playerCards);
        if (pScore <= 21) {
            dealerCards = BlackjackEngine.playDealerTurn(dealerCards, deck);
        }

        // クライアント側で勝敗判定
        const result = BlackjackEngine.judge(playerCards, dealerCards);

        // 画面描画
        this.renderer.renderHand(this.playerHandList, playerCards, false);
        this.renderer.renderHand(this.dealerHandList, dealerCards, false);

        if (this.playerScoreOutput) {
            this.playerScoreOutput.textContent = `${result.playerScore} 点 ${result.playerScore > 21 ? '（バースト）' : ''}`;
        }
        if (this.dealerScoreOutput) {
            this.dealerScoreOutput.textContent = `${result.dealerScore} 点 ${result.dealerScore > 21 ? '（バースト）' : ''}`;
        }
        if (this.resultBanner) {
            this.resultBanner.dataset.outcome = result.outcome;
        }
        if (this.messageOutput) {
            this.messageOutput.textContent = result.message;
        }
    }
}

// --- 起動ディスパッチャー ---
document.addEventListener('DOMContentLoaded', () => {
    const pageType = document.body.dataset.page;
    if (pageType === 'game') {
        new GamePageController();
    } else if (pageType === 'result') {
        new ResultPageController();
    }
});
