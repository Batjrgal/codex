import express from "express";
import { exec } from "child_process";
import cors from "cors";
import path from "path";

const app = express();
app.use(express.json());
app.use(cors());

// Serve downloaded files
app.use("/downloads", express.static(path.resolve("./downloads")));

// Basic root route to avoid 404 at /
app.get("/", (req, res) => {
	res.send("Backend is running. POST /download to start a download.");
});

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
      file: `https://laravel1-production-5b85.up.railway.app/downloads/${title}.mp3`
    });
  });
});

app.listen(process.env.PORT || 8080, () => console.log("🚀 Backend running on https://laravel1-production-5b85.up.railway.app:8080"));
