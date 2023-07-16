$(document).ready(() => {
    //version
    console.log(`jQuery ${$().jquery}`);

    //draggable
    $("img").attr("draggable", false);

    //up arrow button
    $("#up-arrow-button").on("click", () => eel.snakeSetDirection("up")())
        .parent()
        .attr("colspan", 2);
    
    //down arrow button
    $("#down-arrow-button").on("click", () => eel.snakeSetDirection("down")())
        .parent()
        .attr("colspan", 2);
    
    //left arrow button
    $("#left-arrow-button").on("click", () => eel.snakeSetDirection("left")());

    //right arrow buttons
    $("#right-arrow-button").on("click", () => eel.snakeSetDirection("right")());

    //retry button
    const retryButton = $("#retry-button");
    
    retryButton.on("mouseover", (e) => {
        const text = retryButton.text() + "?"
        retryButton.text(text)
    });
    retryButton.on("mouseout", (e) => {
        const text = retryButton.text().slice(0, -1)
        retryButton.text(text);
    });

    retryButton.on("click", () => {
        eel.snakeRetry()();
        window.begin();
    });
});