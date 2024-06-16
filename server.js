const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 3000;
app.use(express.static("templates"));
app.use(bodyParser.json());

app.get("/", (req, res) => {
  fs.readFile("index.html", "utf8", (err, data) => {
    if (err) {
      console.error(`Error reading HTML file: ${err}`);
      res.status(500).send("Internal Server Error");
      return;
    }
    res.send(data);
  });
});

app.post("/save-file", (req, res) => {
  const userInput = req.body.userInput;
  const filePath = "templates/src_doc/program.txt";
  const filePath2 = "templates/flowchart/program.py";

  fs.writeFile(filePath, userInput, (err) => {
    if (err) {
      console.error("Error saving file:", err);
      return res.status(500).send("Failed to save file. Please try again.");
    }
    console.log("File saved successfully in:", filePath);

    fs.writeFile(filePath2, userInput, (err) => {
      if (err) {
        console.error("Error saving file in backup location:", err);
        return res
          .status(500)
          .send("Failed to save file in backup location. Please try again.");
      }
      console.log("File saved successfully in backup location:", filePath2);
      res.sendStatus(200);
    });
  });
});

app.get("/flowchart", (req, res) => {
  exec(
    "python -m pyflowchart templates/flowchart/program.py",
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python command: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`Python command stderr: ${stderr}`);
        return;
      }

      const flowchartCode = stdout.trim();
      res.send(flowchartCode);
    },
  );
});

app.post("/response", (req, res) => {
  const userInput = req.body.userInput;

  exec(
    `python templates/src_doc/rag.py ${userInput}`,
    (error, stdout, stderr) => {
      const output = stdout.trim();
      res.send(output);
    },
  );
});

const db = new sqlite3.Database("chat_history.db");

app.get("/chat-history", (req, res) => {
  db.all("SELECT * FROM chat_history ORDER BY timestamp ASC", (err, rows) => {
    if (err) {
      console.error("Error fetching chat history from database:", err);
      res.status(500).send("Error fetching chat history from database");
    } else {
      res.json(rows);
    }
  });
});

app.post("/clear-chat-history", (req, res) => {
  db.run("DELETE FROM chat_history", (err) => {
    if (err) {
      console.error("Error clearing chat history from database:", err);
      res.status(500).send("Error clearing chat history from database");
    } else {
      res.sendStatus(200);
    }
  });
});

app.post("/save-message", (req, res) => {
  const { message, sender } = req.body;
  db.run(
    "INSERT INTO chat_history (message, sender) VALUES (?, ?)",
    [message, sender],
    (err) => {
      if (err) {
        console.error("Error saving message to database:", err);
        res.status(500).send("Error saving message to database");
      } else {
        res.sendStatus(200);
      }
    },
  );
});

app.post("/run-python", (req, res) => {
  exec(
    "python Code2Logic/main.py",
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python command: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`Python command stderr: ${stderr}`);
        return;
      }

      const output = stdout.trim();
      res.send(output);
    },
  );
});


const server = app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);

  exec(`open http://localhost:${PORT}`);
});

server.on("close", () => {
  console.log("Server closed");
});
