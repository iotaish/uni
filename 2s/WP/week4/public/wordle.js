/**
 * /public/wordle.js
 * サーバーPOST通信と連携した Wordle クライアントロジック
 */

class WordleToast {
    constructor(element) {
        this.el = element;
        this.timer = null;
    }

    show(message, duration = 2000) {
        if (!this.el) return;
        this.el.textContent = message;
        this.el.dataset.visible = 'true';
        clearTimeout(this.timer);
        this.timer = setTimeout(() => {
            this.el.dataset.visible = 'false';
        }, duration);
    }
}

class WordleBoard {
    constructor(container, template) {
        this.container = container;
        this.template = template;
        this.rows = [];
        this.init();
    }

    init() {
        this.container.replaceChildren();
        this.rows = [];
        for (let r = 0; r < 6; r++) {
            const clone = this.template.content.cloneNode(true);
            const row = clone.querySelector('ol');
            this.container.appendChild(row);
            this.rows.push(Array.from(row.querySelectorAll('li')));
        }
    }

    setTile(rowIdx, colIdx, letter) {
        const tile = this.rows[rowIdx]?.[colIdx];
        if (tile) {
            tile.textContent = letter;
            tile.dataset.state = letter ? 'tbd' : 'empty';
        }
    }

    // フリップアニメーションで結果を開示
    revealRow(rowIdx, resultLetters) {
        const row = this.rows[rowIdx];
        if (!row) return;

        resultLetters.forEach((status, colIdx) => {
            const tile = row[colIdx];
            if (!tile) return;

            setTimeout(() => {
                tile.classList.add('flip-in');
                setTimeout(() => {
                    tile.dataset.state = status; // 'correct' | 'present' | 'absent'
                    tile.classList.remove('flip-in');
                    tile.classList.add('flip-out');
                    setTimeout(() => {
                        tile.classList.remove('flip-out');
                    }, 200);
                }, 200);
            }, colIdx * 250);
        });
    }

    shakeRow(rowIdx) {
        const row = this.rows[rowIdx]?.[0]?.parentElement;
        if (!row) return;
        row.animate([
            { transform: 'translateX(0)' },
            { transform: 'translateX(-8px)' },
            { transform: 'translateX(8px)' },
            { transform: 'translateX(-8px)' },
            { transform: 'translateX(8px)' },
            { transform: 'translateX(0)' }
        ], { duration: 320 });
    }
}

class WordleKeyboard {
    constructor(navElement, onKeyPress) {
        this.nav = navElement;
        this.onKeyPress = onKeyPress;
        this.keyElements = new Map();
        this.init();
    }

    init() {
        const buttons = this.nav.querySelectorAll('button[data-key]');
        buttons.forEach(btn => {
            const key = btn.dataset.key;
            this.keyElements.set(key, btn);
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.onKeyPress(key);
            });
        });
    }

    updateKey(letter, status) {
        const btn = this.keyElements.get(letter);
        if (!btn) return;
        const current = btn.dataset.state;
        // 優先度: correct > present > absent
        if (current === 'correct') return;
        if (current === 'present' && status === 'absent') return;
        btn.dataset.state = status;
    }

    reset() {
        this.keyElements.forEach(btn => {
            delete btn.dataset.state;
        });
    }
}

class WordleApp {
    constructor() {
        this.toast = new WordleToast(document.querySelector('[data-role="toast"]'));
        const gridEl = document.querySelector('[data-role="grid"]');
        const rowTemplate = document.querySelector('.row-template');
        this.board = new WordleBoard(gridEl, rowTemplate);

        const keyboardEl = document.querySelector('[data-role="keyboard"]');
        this.keyboard = new WordleKeyboard(keyboardEl, (key) => this.handleInput(key));

        this.restartBtn = document.querySelector('[data-action="restart"]');
        if (this.restartBtn) {
            this.restartBtn.addEventListener('click', () => this.startNewGame());
        }

        this.gameId = null;
        this.currentRow = 0;
        this.currentCol = 0;
        this.currentGuess = '';
        this.isGameOver = false;

        this.bindPhysicalKeyboard();
        this.startNewGame();
    }

    bindPhysicalKeyboard() {
        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey || e.altKey) return;

            // IME対策: e.code を優先してキーボードの物理キーを直接判定
            if (e.code === 'Enter' || e.key === 'Enter') {
                e.preventDefault();
                this.handleInput('ENTER');
                return;
            }

            if (e.code === 'Backspace' || e.key === 'Backspace') {
                e.preventDefault();
                this.handleInput('BACKSPACE');
                return;
            }

            // KeyA ~ KeyZ の物理キーをダイレクトに英大文字へマッピング（日本語入力状態でも確実に動作）
            if (e.code && e.code.startsWith('Key')) {
                const char = e.code.slice(3).toUpperCase();
                if (char.length === 1 && char >= 'A' && char <= 'Z') {
                    e.preventDefault();
                    this.handleInput(char);
                    return;
                }
            }

            // 通常の e.key によるフォールバック
            if (/^[a-zA-Z]$/.test(e.key)) {
                e.preventDefault();
                this.handleInput(e.key.toUpperCase());
            }
        });
    }

    // 1. POST /api/wordle/start でサーバー乱数により単語を選定
    async startNewGame() {
        try {
            const res = await fetch('/api/wordle/start', { method: 'POST' });
            if (!res.ok) throw new Error('通信エラー');
            const data = await res.json();

            this.gameId = data.gameId;
            this.currentRow = 0;
            this.currentCol = 0;
            this.currentGuess = '';
            this.isGameOver = false;

            this.board.init();
            this.keyboard.reset();
            this.toast.show('5文字の単語を当ててください', 2000);
        } catch (err) {
            this.toast.show('ゲーム開始に失敗しました');
        }
    }

    handleInput(key) {
        if (this.isGameOver) return;

        if (key === 'ENTER') {
            this.submitGuess();
        } else if (key === 'BACKSPACE') {
            if (this.currentCol > 0) {
                this.currentCol--;
                this.currentGuess = this.currentGuess.slice(0, -1);
                this.board.setTile(this.currentRow, this.currentCol, '');
            }
        } else if (/^[A-Z]$/.test(key)) {
            if (this.currentCol < 5) {
                this.board.setTile(this.currentRow, this.currentCol, key);
                this.currentGuess += key;
                this.currentCol++;
            }
        }
    }

    // 2. POST /api/wordle/guess で辞書チェック ＆ 正誤判定
    async submitGuess() {
        if (this.currentCol < 5) {
            this.board.shakeRow(this.currentRow);
            this.toast.show('5文字入力してください');
            return;
        }

        try {
            const res = await fetch('/api/wordle/guess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gameId: this.gameId,
                    guess: this.currentGuess
                })
            });

            const data = await res.json();
            if (!res.ok) {
                this.board.shakeRow(this.currentRow);
                this.toast.show(data.error || '辞書にない単語です');
                return;
            }

            // タイルのフリップアニメーション＆色付け
            this.board.revealRow(this.currentRow, data.result);

            // キーボードのキー色更新（少し遅延してタイルと合わせる）
            setTimeout(() => {
                data.guess.split('').forEach((letter, i) => {
                    this.keyboard.updateKey(letter, data.result[i]);
                });
            }, 5 * 250);

            if (data.isWin) {
                this.isGameOver = true;
                setTimeout(() => {
                    this.toast.show(`🎉 お見事！${data.attempt}回目でクリア！`, 5000);
                }, 1400);
            } else if (data.isGameOver) {
                this.isGameOver = true;
                setTimeout(() => {
                    this.toast.show(`残念！正解は 【${data.targetWord}】 でした`, 6000);
                }, 1400);
            } else {
                this.currentRow++;
                this.currentCol = 0;
                this.currentGuess = '';
            }
        } catch (err) {
            this.toast.show('通信エラーが発生しました');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new WordleApp();
});
