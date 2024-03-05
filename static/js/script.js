document.addEventListener("DOMContentLoaded", () => {
    startGame();
    const drawButton = document.getElementById('draw-button');
    const playButton = document.getElementById('play-button');
    const playInput = document.getElementById('play-input');
    const newGameButton = document.getElementById('new-game-button');

    drawButton.addEventListener('click', () => {
        fetch('/draw')
            .then(response => response.json())
            .then(data => {
                displayPlayerHand(data);
                updateDiscardPile(data.top_discard);
                displayComputerHand(data.computer_hand, data.computer_turn.message);
                displayMessage(data);
                displayCardSelection(data.player_hand);
            })
            .catch(error => {
                console.error('Error:', error);
        });
    });

    playButton.addEventListener('click', () => {

        if (playInput.value === '') {
            const messageElement = document.getElementById('chat');
            messageElement.innerHTML += `<p class='error'>Podaj kartę!</p>`;
            return;
        }

        const cardParts = playInput.value.split(' ');  // format: rank suit
        const card = { rank: cardParts[0], suit: cardParts[1] };

        if (cardParts.length !== 2) {
            const messageElement = document.getElementById('chat');
            messageElement.innerHTML += `<p class='error'>Niepoprawny format karty!</p>`;
            return;
        }

        const validRanks = ['5', '6', '7', '8', '9', '10', 'Królowa'];
        var demandedRank = '';

        if (cardParts[0] === 'Walet') {
            while (!validRanks.includes(demandedRank)) {
                demandedRank = prompt("Zagrałeś waleta czego żądasz: " + validRanks.join(", "));
                if (!validRanks.includes(demandedRank)) {
                    alert("Niepoprawna forma. spróbuj ponownie: " + validRanks.join(", "));
                }
            }
            console.log(demandedRank); 
        }

        const validSuits = ['Kier', 'Karo', 'Pik', 'Trefl']
        var demandedSuit = ''


        if (cardParts[0] === 'Ass') {
            while (!validSuits.includes(demandedSuit)) {
                demandedSuit = prompt("Zagrałeś Assa, jakiego koloru żądasz: " + validSuits.join(", "));
                if (!validSuits.includes(demandedSuit)) {
                    alert("Niepoprawna forma. spróbuj ponownie: " + validSuits.join(", "));
                }
            }
            console.log(demandedSuit)
        }
        
        fetch('/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({card: card, demandedRank: demandedRank, demandedSuit: demandedSuit}),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                displayPlayerHand(data);
                updateDiscardPile(data.top_discard);
                displayCardSelection(data.player_hand);
                displayComputerHand(data.computer_hand, data.computer_turn.message);
                displayMessage(data);
            })
            .catch(error => {
                console.error('Error:', error);
        });
    });
    
    newGameButton.addEventListener('click', () => {
        fetch('/new_game', {
            method: 'GET'
        })
            .then(response => response.json())
            .then(data => {
                
                displayPlayerHand(data);
                updateDiscardPile(data.top_discard);
                if (data.computer_turn && data.computer_turn.message) {
                    displayComputerHand(data.computer_hand, data.computer_turn.message);
                } else {
                    displayComputerHand(data.computer_hand, "");
                }
                displayMessage(data);
                displayCardSelection(data.player_hand);
                drawButton.disabled = false;
                playButton.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
        });
    });
});

// AJAX do serwera
function startGame() {
    try {
        fetch('/start')
            .then(response => response.json())
            .then(data => {
                displayPlayerHand(data);
                updateDiscardPile(data.top_discard);
                displayComputerHand(data.computer_hand);
                displayCardSelection(data.player_hand);
            });
    } catch (error) {
        console.log(error);
    }
}

function displayCardSelection(cards) {
    const cardSelectElement = document.getElementById('play-input');
    cardSelectElement.innerHTML = ''; // Wyczyść rękę gracza (nwm czy potrzebne do wywalenia jak cos xpp)
    cards.forEach(card => {
        const option = document.createElement('option');
        option.value = `${card.rank} ${card.suit}`;
        option.textContent = `${card.rank} ${card.suit}`;
        cardSelectElement.appendChild(option);
    })
}

function displayPlayerHand(cards) {
    const messageElement = document.getElementById('chat');
    const handElement = document.getElementById('player-hand');
    if (cards.success === false) {
        messageElement.innerHTML += `<p class='error'>${cards.message}</p>`;
        return;
    }
    if (cards.message === 'Wygrałeś!') {
        let drawButton = document.getElementById('draw-button');
        let playButton = document.getElementById('play-button');
        drawButton.disabled = true;
        playButton.disabled = true;
        messageElement.innerHTML += `<p class='win'>${cards.message}</p>`;
        alert('Wygrałeś! Zacznij nową grę!');
        return;
    }

    if (cards.message === 'kompik czeka') {
        messageElement.innerHTML += `<p class='info'>Komputer skipuje ture</p>`;
    }

    handElement.innerHTML = ''; // Wyczyść rękę gracza (nwm czy potrzebne do wywalenia jak cos xpp)
    cards.player_hand.forEach(card => {
        handElement.innerHTML += `<div class="card">${card.rank} ${card.suit}</div>`; // Wyswietl karty gracza
    });
}

function updateDiscardPile(card) {
    console.log(card);
    
    const discardPileElement = document.getElementById('discard-pile');
    discardPileElement.innerHTML = `<div class="card">Karta na stole: ${card.rank} ${card.suit}</div>`; // Wyswietl ostatnia karte na stosie
}

function displayComputerHand(cards, message) {
    const messageElement = document.getElementById('chat');
    if (!cards) {
        console.error('Invalid or undefined card data');
        return;
    }

    if (message === 'Komputer wygrał!') {
        let drawButton = document.getElementById('draw-button');
        let playButton = document.getElementById('play-button');
        drawButton.disabled = true;
        playButton.disabled = true;
        messageElement.innerHTML += `<p class='win'>${message}</p>`;
        alert('Komputer wygrał! Spróbuj jeszcze raz!');
        return;
    }
    const handleElement = document.getElementById('computer-hand');
    handleElement.innerHTML = ''; 
    handleElement.innerHTML += `<div class="card">Komputer ma ${cards.length} kart</div>`; // Wyswietl liczbę kart w ręce komputera
}

function displayMessage(message) {
    if (!message) {
        console.error('Invalid or undefined message');
        return;
    }
    const messageElement = document.getElementById('chat');
    if (message.message === undefined) {
        messageElement.innerHTML = `<p class='info'>Rozpoczętą nową gierkę!</p>`;
        return;
    }
    if (message.message.includes('Czekasz') || (message.computer_turn && message.computer_turn.message.includes('czeka'))) {
        messageElement.innerHTML += `<p class='info'>${message.message}<br>${message.computer_turn ? message.computer_turn.message : ''}</p>`;
    } else {
        messageElement.innerHTML += `<p>${message.message}<br>${message.computer_turn ? message.computer_turn.message : ''}</p>`;
    }
}