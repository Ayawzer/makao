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
        
        fetch('/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({card: card}),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
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
    const handElement = document.getElementById('player-hand');
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
        messageElement.innerHTML += `<p class='win'>${cards.message}</p>`;
        alert('Komputer wygrał! Spróbuj jeszcze raz!');
        return;
    }
    const handleElement = document.getElementById('computer-hand');
    handleElement.innerHTML = ''; // Wyczyść rękę komputera (nwm czy potrzebne do wywalenia jak cos xpp)
    //cards.forEach(card => { //for future debbuging
    //    handleElement.innerHTML += `<div class="card">${card.rank} of ${card.suit}</div>`; // Wyswietl karty gracza
    //}); // Wyswietl liczbę kart w ręce komputera
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
    messageElement.innerHTML += `<p>${message.message}<br>${message.computer_turn.message}</p>`; // Wyswietl wiadomosc
}