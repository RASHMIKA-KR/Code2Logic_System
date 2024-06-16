document.addEventListener("DOMContentLoaded", function () {
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-button");
  const chatMessages = document.getElementById("chat-messages");
  const importButton = document.getElementById("import-button");
  const flowchartButton = document.getElementById("flowchart-button");
  const clearHistoryButton = document.getElementById("clear-history-button");
  const runPythonButton = document.getElementById("run-python-button");

  runPythonButton.addEventListener("click", function () {
    fetch("/run-python", {
      method: "POST",
    })
      .then((response) => response.text())
      .then((output) => {
        console.log("Python script executed:", output);
        // Handle the output if needed
      })
      .catch((error) => console.error("Error running Python script:", error));
  });
  

  function codetoflow(){
    

  }
  function confirmClearChatHistory() {
    const confirmation = confirm(
      "Are you sure you want to clear the chat history?",
    );
    if (confirmation === true) {
      clearChatHistory();
    } else {
      console.log("Clear chat history cancelled");
    }
  }

  function clearChatHistory() {
    fetch("/clear-chat-history", {
      method: "POST",
    })
      .then((response) => {
        if (response.ok) {
          console.log("Chat history cleared successfully");
          chatMessages.innerHTML = "";
        } else {
          console.error("Failed to clear chat history");
        }
      })
      .catch((error) => console.error("Error clearing chat history:", error));
  }

  function fetchAndFillChatHistory() {
    fetch("/chat-history")
      .then((response) => response.json())
      .then((data) => {
        chatMessages.innerHTML = "";
        data.forEach((message) => {
          appendMessage(message.message, message.sender);
        });
      })
      .catch((error) => console.error("Error fetching chat history:", error));
  }

  function appendMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.classList.add(sender);
    messageElement.innerText = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  const fetchHistoryButton = document.getElementById("fetch-history-button");
  fetchHistoryButton.addEventListener("click", fetchAndFillChatHistory);

  clearHistoryButton.addEventListener("click", confirmClearChatHistory);

  function sendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText !== "") {
      appendMessage(messageText, "user");
      messageInput.value = "";
      saveToDatabase(messageText, "user");

      fetch("/response", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userInput: messageText }),
      })
        .then((response) => response.text())
        .then((output) => {
          appendMessage(output, "bot");
          saveToDatabase(output, "bot");
        })
        .catch((error) => console.error("Error sending message:", error));
    }
  }

  function saveToDatabase(message, sender) {
    fetch("/save-message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message, sender: sender }),
    })
      .then((response) => {
        if (response.ok) {
          console.log("Message saved to database successfully");
        } else {
          console.error("Failed to save message to database");
        }
      })
      .catch((error) =>
        console.error("Error saving message to database:", error),
      );
  }

  sendButton.addEventListener("click", sendMessage);

  messageInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

  importButton.addEventListener("click", function () {
    const userInput = prompt("Enter text to save to file:");
    if (userInput !== null) {
      if (userInput.trim() !== "") {
        appendMessage(userInput, "user");
        fetch("/save-file", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ userInput: userInput }),
        })
          .then((response) => {
            if (response.ok) {
              console.log("File saved successfully");
            } else {
              console.error("Failed to save file");
            }
          })
          .catch((error) => console.error("Error saving file:", error));
      } else {
        alert("Invalid input. Please enter some text.");
      }
    }
  });

  function loadFlowchart() {
    fetch("/flowchart")
      .then((response) => response.text())
      .then((code) => {
        var chartDiv = document.createElement("div");
        chartDiv.setAttribute("id", "canvas");
        chatMessages.appendChild(chartDiv);

        chart = flowchart.parse(code);
        chart.drawSVG("canvas", {
          x: 0,
          y: 0,
          "line-width": 3,
          "line-length": 50,
          "text-margin": 10,
          "font-size": 14,
          "font-family": "Helvetica",
          "font-color": "black",
          "line-color": "black",
          "element-color": "black",
          fill: "white",
          "yes-text": "yes",
          "no-text": "no",
          "arrow-end": "block",
          scale: 1,
          symbols: {
            start: {
              "font-size": 14,
              "font-color": "yellow",
              "element-color": "blue",
              fill: "green",
              class: "start-element",
            },
            inputoutput: {
              "font-color": "black",
              "element-color": "black",
              fill: "bisque",
            },
            operation: {
              "font-color": "black",
              "element-color": "black",
              fill: "linen",
            },
            condition: {
              "font-color": "red",
              "element-color": "black",
              fill: "yellow",
            },
            end: {
              "font-size": 20,
              class: "end-element",
            },
          },
          flowstate: {
            request: { fill: "blue" },
            invalid: { fill: "#444444" },
            approved: {
              fill: "#58C4A3",
              "font-size": 12,
              "yes-text": "APPROVED",
              "no-text": "n/a",
            },
            rejected: {
              fill: "#C45879",
              "font-size": 12,
              "yes-text": "n/a",
              "no-text": "REJECTED",
            },
          },
        });
      })
      .catch((error) => console.error("Error fetching flowchart:", error));
  }

  flowchartButton.addEventListener("click", function () {
    loadFlowchart();
  });



});
