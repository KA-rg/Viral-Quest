const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");
const path = require("path");

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "../frontend")));

app.post("/api/analyze", (req, res) => {
  const { username, max_posts, mode } = req.body; // mode = "mock" or "real"

  if (!username) return res.json({ status: "error", message: "Username required" });

  const py = spawn("python", [
    path.join(__dirname, "instaAnalysis.py"),
    username,
    max_posts || 4,
    mode || "mock"
  ]);

  let data = "";
  py.stdout.on("data", chunk => { data += chunk.toString(); });
  py.stderr.on("data", chunk => { console.error(chunk.toString()); });

  py.on("close", () => {
    try {
      const json = JSON.parse(data);
      res.json(json);
    } catch (err) {
      res.json({ status: "error", message: "Python error" });
    }
  });
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
