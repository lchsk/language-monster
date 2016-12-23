module.exports = {
    "extends": "eslint:recommended",
    "rules": {
        "indent": ["error", 4],
        "no-console": 0
    },
    "env": {
        "browser": true
    },
    "globals": {
        "MONSTER": true,
        "PIXI": true,
        "$": true,
        "jQuery": true,
        "Vue": true,
        "smoothScroll": true
    }
};
