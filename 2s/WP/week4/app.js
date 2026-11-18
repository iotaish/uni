import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

//app.set('view engine', 'ejs');
app.use("/public", express.static(path.join(__dirname, "/public")));

app.get("/", (req, res) => {
  res.write('Hello, World\n');
});

app.use(function(req, res, next) {
  res.status(404).send('ページが見つかりません');
});

app.listen(8080, () => console.log("Example app listening on port 8080!"));
