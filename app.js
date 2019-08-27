let express = require("express"),
    app = express();

const execSync = require('child_process').execSync;

app.use(express.static("public"));
app.set("view engine", "ejs");

app.get("/", function (req, res) {
    res.render("index");
});

app.get("/duplicate", function (req, res) {	
	execSync('DisplaySwitch.exe /clone', { encoding: 'utf-8' });   
});

app.get("/internal", function (req, res) {	
	execSync('DisplaySwitch.exe /internal', { encoding: 'utf-8' });   
});

app.listen(3000, function () {
    console.log("Loading awesomeness");
});