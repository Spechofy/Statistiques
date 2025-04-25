const langdetect = require('langdetect');  // Importer langdetect

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'chore']
    ],
    'type-empty': [2, 'never'],
    'lang-id': [2, 'always', 'en']
  },
  plugins: [
    {
      rules: {
        'lang-id': ({ raw }) => {
          const detected = langdetect.detect(raw); // Utiliser langdetect pour la détection de langue
          if (detected[0].lang !== 'en') {  // Vérifier si la langue détectée est 'en' pour l'anglais
            return [false, 'The commit message must be written in English.'];
          }
          return [true]; // Si l'anglais est détecté, valider le commit
        }
      }
    }
  ]
};
