import express from "express";
import { exec } from "child_process";
import cors from "cors";
import path from "path";

const app = express();
app.use(express.json());
app.use(cors());

app.post("/download", (req, res) => {
  const { url } = req.body;
  if (!url) return res.json({ success: false, error: "No URL provided" });

  exec(`spotdl "${url}" --output ./downloads`, (error, stdout, stderr) => {
    if (error) {
      return res.json({ success: false, error: stderr });
    }

    const match = stdout.match(/Downloading (.*?) by (.*?)\n/);
    const title = match ? `${match[1]} - ${match[2]}` : "Song";

    res.json({
      success: true,
      title,
      file: `http://localhost:5000/downloads/${title}.mp3`
    });
  });
});

app.listen(5000, () => console.log("🚀 Backend running on http://localhost:5000"));
