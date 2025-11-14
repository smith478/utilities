$(document).ready(function() {
    var board = null;
    var game = new Chess();

    function getAnalysis() {
        $.ajax({
            url: '/analyze',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'fen': game.fen() }),
            success: function(response) {
                $('#stockfish-move').text(response.best_move);
                $('#llm-explanation').html(marked.parse(response.explanation));
            },
            error: function() {
                console.log("Error getting analysis from server");
                $('#stockfish-move').text('N/A');
                $('#llm-explanation').text('Could not get analysis from server.');
            }
        });
    }

    function onDragStart(source, piece, position, orientation) {
        // do not pick up pieces if the game is over
        if (game.game_over()) return false;
    }

    function onDrop(source, target) {
        // see if the move is legal
        var move = game.move({
            from: source,
            to: target,
            promotion: 'q' // NOTE: always promote to a queen for simplicity
        });

        // illegal move
        if (move === null) return 'snapback';

        // get analysis for the new position
        getAnalysis();
    }

    // update the board position after the piece snap
    function onSnapEnd() {
        board.position(game.fen());
    }

    var config = {
        draggable: true,
        position: 'start',
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd
    };
    board = Chessboard('board', config);

    $('#undo-button').on('click', function() {
        game.undo();
        board.position(game.fen());
        getAnalysis();
    });

    // Get analysis for the starting position
    getAnalysis();
});
