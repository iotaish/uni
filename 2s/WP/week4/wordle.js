/**
 * wordle.js - サーバー側 Wordle 単語選定・辞書判定モジュール
 */

// 正解候補となる一般的な5文字英単語（大文字）
const TARGET_WORDS = [
    'APPLE', 'BEACH', 'BRAIN', 'BREAD', 'CHAIR', 'CHEST', 'CLOCK', 'CLOUD',
    'DANCE', 'DREAM', 'EARTH', 'EAGLE', 'FIELD', 'FLAME', 'FRUIT', 'GLASS',
    'GRAPE', 'GREEN', 'HEART', 'HOUSE', 'IMAGE', 'JUICE', 'KNIFE', 'LEMON',
    'LIGHT', 'MAGIC', 'MONEY', 'MUSIC', 'NIGHT', 'OCEAN', 'PAINT', 'PEACE',
    'PHONE', 'PIANO', 'PLANT', 'QUEEN', 'RADIO', 'RIVER', 'ROUND', 'SHINE',
    'SMILE', 'SPACE', 'STAGE', 'STORM', 'SUGAR', 'SWEET', 'TABLE', 'TIGER',
    'TRAIN', 'VOICE', 'WATER', 'WHITE', 'WORLD', 'YOUTH', 'ZEBRA', 'ALERT',
    'ARGUE', 'ASSET', 'BASIC', 'BLOCK', 'BLOOD', 'BOARD', 'BROWN', 'BUILD',
    'CABLE', 'CARRY', 'CATCH', 'CAUSE', 'CHAIN', 'CHARM', 'CHIEF', 'CIVIL',
    'CLEAR', 'CLIMB', 'CLOSE', 'COAST', 'COVER', 'CROWD', 'DAILY', 'DELAY',
    'DOUBT', 'DRAFT', 'DRIVE', 'ENTRY', 'EQUAL', 'ERROR', 'EVENT', 'EXACT',
    'FAITH', 'FIBER', 'FINAL', 'FOCUS', 'FORCE', 'FRAME', 'FRESH', 'FRONT',
    'GIANT', 'GRACE', 'GRAND', 'GRANT', 'GROUP', 'GUIDE', 'HAPPY', 'HEAVY',
    'HOTEL', 'HUMAN', 'IDEAL', 'INDEX', 'INPUT', 'ISSUE', 'JUDGE', 'LABEL',
    'LAYER', 'LEARN', 'LIMIT', 'LOCAL', 'LUCKY', 'LUNCH', 'MAJOR', 'MARCH',
    'MATCH', 'METAL', 'MODEL', 'MOTOR', 'MOUNT', 'MOUSE', 'NOVEL', 'NURSE',
    'OFFER', 'ORDER', 'OTHER', 'PANEL', 'PAPER', 'PARTY', 'PHASE', 'PILOT',
    'POINT', 'POWER', 'PRESS', 'PRICE', 'PRIDE', 'PRIME', 'PRIZE', 'PROOF',
    'PROUD', 'QUICK', 'QUIET', 'RAISE', 'RANGE', 'RAPID', 'RATIO', 'REACH',
    'READY', 'RIGHT', 'ROUTE', 'SCALE', 'SCENE', 'SCOPE', 'SCORE', 'SENSE',
    'SHAPE', 'SHARE', 'SHIFT', 'SHIRT', 'SHOCK', 'SHOOT', 'SHORT', 'SIGHT',
    'SKILL', 'SLEEP', 'SMART', 'SOLID', 'SOLVE', 'SOUND', 'SOUTH', 'SPARE',
    'SPEAK', 'SPEED', 'SPEND', 'SPLIT', 'SPORT', 'STAFF', 'STAND', 'START',
    'STATE', 'STEAM', 'STEEL', 'STICK', 'STILL', 'STOCK', 'STONE', 'STORE',
    'STUDY', 'STYLE', 'SUPER', 'TASTE', 'THEME', 'THING', 'TITLE', 'TOTAL',
    'TOUCH', 'TOWER', 'TRACK', 'TRADE', 'TREAT', 'TREND', 'TRIAL', 'TRUST',
    'TRUTH', 'UNCLE', 'UNION', 'UNITY', 'UPPER', 'URBAN', 'VALUE', 'VIDEO',
    'VIRUS', 'VISIT', 'VITAL', 'WASTE', 'WATCH', 'WHEEL', 'WHOLE', 'WOUND'
];

// 有効な入力単語セット（TARGET_WORDSを含め、より広範に受け付ける）
const VALID_WORDS = new Set(TARGET_WORDS);

// 進行中のゲーム管理（インメモリ）
const games = new Map();

/**
 * 新規ゲームの開始 (POST /api/wordle/start)
 * 乱数（Math.random）を用いて正解単語を選定
 */
function startWordleGame() {
    const randomIndex = Math.floor(Math.random() * TARGET_WORDS.length);
    const targetWord = TARGET_WORDS[randomIndex];

    const gameId = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    games.set(gameId, {
        targetWord,
        guesses: [],
        maxGuesses: 6,
        createdAt: Date.now()
    });

    // 1時間以上古いゲームセッションを掃除
    const oneHourAgo = Date.now() - 3600000;
    for (const [id, data] of games.entries()) {
        if (data.createdAt < oneHourAgo) games.delete(id);
    }

    return {
        gameId,
        wordLength: 5,
        maxGuesses: 6
    };
}

/**
 * 推測の判定 (POST /api/wordle/guess)
 * @param {string} gameId
 * @param {string} rawGuess 5文字の推測英単語
 */
function evaluateGuess(gameId, rawGuess) {
    const game = games.get(gameId);
    if (!game) {
        return { error: 'ゲームセッションが見つかりません。最初からやり直してください。' };
    }

    const guess = (rawGuess || '').toUpperCase().trim();
    if (guess.length !== 5) {
        return { error: '単語は5文字で入力してください。' };
    }

    if (!VALID_WORDS.has(guess)) {
        return { error: '辞書にない単語です。' };
    }

    if (game.guesses.length >= game.maxGuesses) {
        return { error: '既にゲームが終了しています。' };
    }

    const target = game.targetWord;
    const result = new Array(5).fill('absent'); // 'correct' | 'present' | 'absent'
    const targetLetters = target.split('');
    const guessLetters = guess.split('');

    // 1巡目: 緑（位置も文字も一致 = correct）を判定
    for (let i = 0; i < 5; i++) {
        if (guessLetters[i] === targetLetters[i]) {
            result[i] = 'correct';
            targetLetters[i] = null; // カウント済みとして消費
            guessLetters[i] = null;
        }
    }

    // 2巡目: 黄（文字は含まれるが位置が違う = present）を判定
    for (let i = 0; i < 5; i++) {
        if (guessLetters[i] !== null) {
            const foundIdx = targetLetters.indexOf(guessLetters[i]);
            if (foundIdx !== -1) {
                result[i] = 'present';
                targetLetters[foundIdx] = null; // 消費
            }
        }
    }

    game.guesses.push({ guess, result });

    const isWin = guess === target;
    const isGameOver = isWin || (game.guesses.length >= game.maxGuesses);

    const response = {
        guess,
        result, // ['correct', 'present', 'absent', ...]
        attempt: game.guesses.length,
        isWin,
        isGameOver
    };

    if (isGameOver) {
        response.targetWord = target; // ゲーム終了時に正解を開示
        games.delete(gameId);
    }

    return response;
}

export {
    startWordleGame,
    evaluateGuess
};
