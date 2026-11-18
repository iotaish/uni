/**
 * /public/blackjack.js
 * サーバーPOST通信と連携し、クライアント側で主要なゲーム演算・状態管理を行うモジュール
 */

const SUIT_MAP = {
    'S': { symbol: '♠', isRed: false },
    'H': { symbol: '♥', isRed: true },
    'D': { symbol: '♦', isRed: true },
    'C': { symbol: '♣', isRed: false }
};

const RANK_LABELS = {
    1: 'A',
    11: 'J',
    12: 'Q',
    13: 'K'
};

class CardModel {
    constructor(id) {
        this.id = id;
        const [suitCode, numStr] = id.split('_');
        this.suitCode = suitCode;
        this.num = parseInt(numStr, 10);
        const suit = SUIT_MAP[suitCode] || { symbol: '?', isRed: false };
        this.symbol = suit.symbol;
        this.isRed = suit.isRed;
        this.label = RANK_LABELS[this.num] || String(this.num);
    }
}

class BlackjackClientEngine {
    /**
     * 手札の合計点数を計算（Aの1点/11点動的最適化）
     */
    static calculateScore(cardModels) {
        let score = 0;
        let aceCount = 0;

        for (const card of cardModels) {
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
     * 勝敗の判定演算
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

        return { pScore, dScore, outcome, message };
    }
}

class BlackjackApp {
    constructor() {
        this.template = document.querySelector('.card-template');
        this.startBtn = document.querySelector('[data-action="start"]');
        this.hitBtn = document.querySelector('[data-action="hit"]');
        this.standBtn = document.querySelector('[data-action="stand"]');
        this.restartBtn = document.querySelector('[data-action="restart"]');

        this.playerHandEl = document.querySelector('[data-role="player-hand"]');
        this.dealerHandEl = document.querySelector('[data-role="dealer-hand"]');
        this.playerScoreEl = document.querySelector('[data-role="player-score"]');
        this.dealerScoreEl = document.querySelector('[data-role="dealer-score"]');

        this.resultBannerEl = document.querySelector('[data-role="result-banner"]');
        this.resultMsgEl = document.querySelector('[data-role="result-message"]');
        this.resPlayerHandEl = document.querySelector('[data-role="result-player-hand"]');
        this.resDealerHandEl = document.querySelector('[data-role="result-dealer-hand"]');
        this.resPlayerScoreEl = document.querySelector('[data-role="result-player-score"]');
        this.resDealerScoreEl = document.querySelector('[data-role="result-dealer-score"]');

        this.gameId = null;
        this.playerCards = [];
        this.dealerVisibleCard = null;

        this.bindEvents();
        this.bindKeyboardShortcuts();
    }

    bindEvents() {
        if (this.startBtn) this.startBtn.addEventListener('click', () => this.startGame());
        if (this.hitBtn) this.hitBtn.addEventListener('click', () => this.hit());
        if (this.standBtn) this.standBtn.addEventListener('click', () => this.stand());
        if (this.restartBtn) this.restartBtn.addEventListener('click', () => this.setState('start'));
    }

    bindKeyboardShortcuts() {
        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            const currentState = document.body.dataset.state;

            if (currentState === 'start') {
                if (e.code === 'Enter' || e.code === 'Space') {
                    e.preventDefault();
                    this.startGame();
                }
            } else if (currentState === 'playing') {
                if (e.code === 'KeyH' || e.key === 'h' || e.key === 'H' || e.code === 'Space') {
                    e.preventDefault();
                    if (!this.hitBtn.disabled) this.hit();
                } else if (e.code === 'KeyS' || e.key === 's' || e.key === 'S' || e.code === 'Enter') {
                    e.preventDefault();
                    if (!this.standBtn.disabled) this.stand();
                }
            } else if (currentState === 'result') {
                if (e.code === 'Enter' || e.code === 'Space') {
                    e.preventDefault();
                    this.setState('start');
                }
            }
        });
    }

    setState(state) {
        document.body.dataset.state = state;
    }

    createCardElement(card, isHidden = false) {
        const clone = this.template.content.cloneNode(true);
        const item = clone.querySelector('li');

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
            container.appendChild(this.createCardElement(card, isHidden));
        });
    }

    // 1. POST /api/blackjack/start でサーバー乱数デッキから初期手札を取得
    async startGame() {
        this.startBtn.disabled = true;
        try {
            const res = await fetch('/api/blackjack/start', { method: 'POST' });
            if (!res.ok) throw new Error('ゲーム開始通信に失敗しました');
            const data = await res.json();

            this.gameId = data.gameId;
            this.playerCards = data.player.map(id => new CardModel(id));
            this.dealerVisibleCard = new CardModel(data.dealerVisible);

            this.hitBtn.disabled = false;
            this.standBtn.disabled = false;
            this.setState('playing');
            this.updatePlayingView();

            // クライアント側で即時ブラックジャック判定
            const initialScore = BlackjackClientEngine.calculateScore(this.playerCards);
            if (initialScore === 21) {
                // ナチュラルBJなら自動でStandへ進む
                setTimeout(() => this.stand(), 800);
            }
        } catch (err) {
            alert(err.message);
        } finally {
            this.startBtn.disabled = false;
        }
    }

    // 2. POST /api/blackjack/hit で山札から1枚取得
    async hit() {
        this.hitBtn.disabled = true;
        try {
            const res = await fetch('/api/blackjack/hit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gameId: this.gameId })
            });
            if (!res.ok) throw new Error('ドロー通信に失敗しました');
            const data = await res.json();

            this.playerCards.push(new CardModel(data.card));
            this.updatePlayingView();

            // クライアント側でスコア＆バースト判定
            const score = BlackjackClientEngine.calculateScore(this.playerCards);
            if (score > 21) {
                // バーストしたら即終了して結果画面へ
                this.hitBtn.disabled = true;
                this.standBtn.disabled = true;
                setTimeout(() => this.showResult([]), 600);
            } else {
                this.hitBtn.disabled = false;
            }
        } catch (err) {
            alert(err.message);
            this.hitBtn.disabled = false;
        }
    }

    // 3. POST /api/blackjack/stand でディーラーの最終手札を取得
    async stand() {
        this.hitBtn.disabled = true;
        this.standBtn.disabled = true;
        try {
            const res = await fetch('/api/blackjack/stand', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gameId: this.gameId })
            });
            if (!res.ok) throw new Error('勝負通信に失敗しました');
            const data = await res.json();

            const dealerCards = data.dealerCards.map(id => new CardModel(id));
            this.showResult(dealerCards);
        } catch (err) {
            alert(err.message);
            this.hitBtn.disabled = false;
            this.standBtn.disabled = false;
        }
    }

    // ゲーム画面の描画更新（クライアント側でスコア計算）
    updatePlayingView() {
        this.renderHand(this.playerHandEl, this.playerCards, false);
        const pScore = BlackjackClientEngine.calculateScore(this.playerCards);
        this.playerScoreEl.textContent = `${pScore} 点`;

        // ディーラー（1枚表示、1枚伏せ）
        this.renderHand(this.dealerHandEl, [this.dealerVisibleCard, null], true);
        const visibleScore = this.dealerVisibleCard.num === 1 ? 11 : Math.min(this.dealerVisibleCard.num, 10);
        this.dealerScoreEl.textContent = `${visibleScore} 点 + ?`;
    }

    // 4. 結果画面の描画（クライアント側で勝敗判定を演算）
    showResult(dealerCards) {
        // バースト等で dealerCards が空の場合、見えていたカードのみで判定
        const finalDealerCards = dealerCards.length > 0 ? dealerCards : [this.dealerVisibleCard];
        const result = BlackjackClientEngine.judge(this.playerCards, finalDealerCards);

        this.renderHand(this.resPlayerHandEl, this.playerCards, false);
        this.renderHand(this.resDealerHandEl, finalDealerCards, false);

        this.resPlayerScoreEl.textContent = `${result.pScore} 点 ${result.pScore > 21 ? '（バースト）' : ''}`;
        this.resDealerScoreEl.textContent = `${result.dScore} 点 ${result.dScore > 21 ? '（バースト）' : ''}`;

        this.resultBannerEl.dataset.outcome = result.outcome;
        this.resultMsgEl.textContent = result.message;

        this.setState('result');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new BlackjackApp();
});
