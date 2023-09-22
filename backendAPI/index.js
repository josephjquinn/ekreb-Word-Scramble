// Joseph Quinn
// scrabbleAPI

// This Node.js Backend server serves as the backend for my Word Scramble Game. It handles the following functions for the python GUI:
//
//  Word Generation:
//  	•	It generates scrambled words of varying lengths (3 to 6 letters) that players need to unscramble.
//  Word Validation:
//  	•	It validates players' word guesses to check if they match the original word. It determines whether a guess is correct or not.
//  Hints:
//  	•	It provides hints to players when requested. These hints may include information about the part of speech, the starting letter, or the definition of the word.
//  High Score Leaderboard:
// 	•	It maintains a leaderboard that stores and updates high scores achieved by players. Players can compete to achieve the highest scores in the game.
//  API Endpoints:
//  	•	It exposes various API endpoints that the frontend interacts with to request words, hints, solutions, and leaderboard data.
//  Score Calculation:
//  	•	It calculates and updates players' scores based on factors such as the length of the unscrambled word, time taken, and the use of hints.
//  Server Status Check:
// 	•	It provides a status check to ensure that the frontend can connect to the server. If the server is not running, it alerts the frontend.
//  Communication with Frontend:
// 	•	It communicates with the React frontend through HTTP requests and responses, serving as the intermediary between the game logic and the user interface.


//setting up required packages and setting port number
const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 3000;
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
const fs = require('fs');
const axios = require('axios');
const {response} = require("express");

// file path for dependencies (words.txt for word selection & leaderboard.txt for leaderboard scores)
const path = require('path');
const filePath = path.join(__dirname, 'words.txt');
const leaderboardFilename = path.join(__dirname, 'leaderboard.txt');


let currentWord = '';
let scramble = '';
let round = 0;
let complete = 0;
let round_accuracy_percents = [];



// get home request to display api title (not necessary for game)
app.get('/', (req, res) => {
   res.send("Random Word Generator") ;
});


// initializes game variables
app.get('/session', (req, res) => {
    res.send("Operational") ;
    round = 0;
    complete = 0;
    round_accuracy_percents = []
});

// post request that will be sent from frontend to check if a word is in the correct position,
// also returns both the position data, and the similarity % for our guess and solution
app.post('/check-word', (req, res) => {
    const inputWord = req.body.word;
    const solution = currentWord
    const word_score = checkScrambledWord(inputWord, solution)

    if (inputWord === solution) {
        res.json({ result: 'correct',
                score: word_score});
        complete++;
    } else {
        res.json({ result: 'incorrect',
            score: word_score});
    }
});


// post request that will be sent from frontend to get a word. Takes the requested word letter length as a parameter and responds with the word from the herokuapp API
app.post('/get-word', async (req, res) =>
{
    const inputData = parseInt(req.body.letters, 10);
    const words = readTextFile(filePath, inputData);
    const target = getRandomWord(words)

    currentWord = '' + target
    scramble = scrambleWord(currentWord)
    round++;
    res.json({word: scramble});
});


// returns the accuracy % calculations
app.post('/accuracy', (req, res) => {
    const guess_attempts = req.body.guess_attempts;
    const cp = (complete/round)*100;
    const ra = (1/guess_attempts)*100;

    round_accuracy_percents.push(ra)
    let sum = 0;
    for (let i = 0; i < round_accuracy_percents.length; i++) {
        sum += round_accuracy_percents[i];
    }

    const ga = sum / round_accuracy_percents.length;

    res.json({ completion: cp,
        round_accuracy: ra,
    game_accuracy: ga});
});


// returns the speech type of the solution (hint 1 button)
app.get('/hint-1', async (req, res) => {
    try {
        const apiUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${currentWord}`;
        const response = await axios.get(apiUrl);

        if (Array.isArray(response.data) && response.data.length > 0) {
            const meanings = response.data[0].meanings;

            if (meanings && Array.isArray(meanings) && meanings.length > 0) {
                const partOfSpeech = meanings[0].partOfSpeech;
                res.json({ partOfSpeech });
            } else {
                res.status(404).json({ error: 'No meanings found for the word.' });
            }
        } else {
            res.status(404).json({ error: 'Word not found in the dictionary API.' });
        }
    } catch (error) {
        console.error('Error fetching hints:', error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});


// returns the first letter of the solution (hint 2 button)
app.get('/hint-2', (req, res) => {
    const first_letter = currentWord[0]
    res.send(first_letter) ;
});


// returns the definition of the solution (hint 3 button)
app.get('/hint-3', async (req, res) => {
    try {
        const apiUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${currentWord}`;
        const response = await axios.get(apiUrl);

        if (Array.isArray(response.data) && response.data.length > 0) {
            const meanings = response.data[0].meanings;

            if (meanings && Array.isArray(meanings) && meanings.length > 0) {
                const definitions = meanings[0].definitions;

                if (definitions && Array.isArray(definitions) && definitions.length > 0) {
                    const definition = definitions[0].definition;
                    res.json({ definition });
                } else {
                    res.status(404).json({ error: 'No definitions found for the word.' });
                }
            } else {
                res.status(404).json({ error: 'No meanings found for the word.' });
            }
        } else {
            res.status(404).json({ error: 'Word not found in the dictionary API.' });
        }
    } catch (error) {
        console.error('Error fetching hints:', error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});


// returns solution(ONLY FOR DISPLAY PURPOSES)
app.get('/get-solution', (req, res) => {
    res.send(currentWord) ;
});


// returns leaderboard as map array
app.get('/get-leaderboard', (req, res) => {
    const highScores = readHighScores(leaderboardFilename);
    const updatedScoresText = highScores
        .map((entry, index) => `${index + 1}. ${entry.name}, ${entry.score}`)
        .join('\n');
    res.json({ leaderboard: updatedScoresText });
});


// Route to update the leaderboard with current round score and username
app.post('/update-leaderboard', (req, res) => {
    const { username, newScore } = req.body;
    if (!username || typeof newScore !== 'number') {
        res.status(400).json({ error: 'Invalid request data.' });
        return;
    }

    updateLeaderboard(username, newScore);
    res.json({ message: 'Leaderboard updated successfully.' });
});


// function that takes the solution and randomizes the letter positions
function scrambleWord(word) {
    let originalWord = word.split('');
    let scrambledWord;

    do {
        let charList = [...originalWord];
        shuffleArray(charList);
        scrambledWord = charList.join('');
    } while (scrambledWord === word);

    return scrambledWord;
}

// function to shuffle an array using Fisher-Yates algorithm
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]]; // Swap elements
    }
}


// function to return both the position data, and the similarity % for our guess and solution
function checkScrambledWord(scrambledWord, originalWord) {
    if (scrambledWord.length !== originalWord.length) {
        return "Input words have different lengths";
    }

    let result = '';
    for (let i = 0; i < scrambledWord.length; i++) {
        if (scrambledWord[i] === originalWord[i]) {
            result += '*';
        } else {
            result += '-';
        }
    }

    let matchingCharacters = 0;
    for (let i = 0; i < scrambledWord.length; i++) {
        if (scrambledWord[i] === originalWord[i]) {
            matchingCharacters++;
        }
    }
    const similarityPercentage = (matchingCharacters / originalWord.length) * 100;
    return {
        code: result,
        similarity: similarityPercentage.toFixed(2) + '%'
    };
}


// function to return txt file as string array for manipulation purposes
function readTextFile(filePath, wordLength) {
    try {
        const fileContent = fs.readFileSync(filePath, 'utf8');
        const lines = fileContent.split('\n');
        const words = [];

        lines.forEach((line) => {
            const lineWords = line.split(/\s+/); // Split line into words
            words.push(...lineWords.filter((word) => word.length === wordLength));
        });

        return words;
    } catch (error) {
        console.error('Error reading the file:', error);
        return null;
    }
}


// function to select a random word from a string array
function getRandomWord(wordArray) {
    if (!Array.isArray(wordArray) || wordArray.length === 0) {
        return null;
    }
    const randomIndex = Math.floor(Math.random() * wordArray.length);
    return wordArray[randomIndex];
}


// function to read high scores from the file and convert it into a malleable format
function readHighScores(filename) {
    try {
        const data = fs.readFileSync(filename, 'utf-8');
        const lines = data.split('\n');
        const highScores = lines
            .map(line => line.trim())
            .filter(line => line.length > 0) // Filter out empty lines
            .map(line => {
                const [name, score] = line.split(', ');
                return { name, score: parseInt(score) };
            });
        return highScores;
    } catch (error) {
        console.error('Error reading high scores:', error);
        return [];
    }
}


// function to update leaderboard with new score and username and keeps the top 10
function updateLeaderboard(username, newScore) {
    const highScores = readHighScores(leaderboardFilename);
    highScores.push({ name: username, score: newScore });
    highScores.sort((a, b) => b.score - a.score);
    const N = 10;
    const topScores = highScores.slice(0, N);
    try {
        const leaderboardText = topScores.map(entry => `${entry.name}, ${entry.score}`).join('\n');
        fs.writeFileSync(leaderboardFilename, leaderboardText);
    } catch (error) {
        console.error('Error updating leaderboard:', error);
    }
}


// port configuration
app.listen( 3000, ()  => console.log("Listening on port 3000..."));
