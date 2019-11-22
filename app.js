let express = require("express"),
	fs = require('fs'),
    url = require('url'),
    bodyParser = require('body-parser'),
    multer  = require('multer'),
    createCsvWriter = require('csv-writer').createObjectCsvWriter,
    app = express();

const exec = require('child_process').exec;

// store in cookie
let CPid = 0;
let CSid = 0;
let strFileName = 0;
let CType = "";

let CTypes = { "F" : "EFT", "R" : "ERT", "P" : "EPT"}
let csvWriter = {};

app.use(bodyParser.json());       // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({    // to support URL-encoded bodies
    extended: true
}));

const upload = multer();

app.use(express.static("public"));
app.set("view engine", "ejs");

app.get("/", function (req, res) {
    res.render("index");
});

app.post("/togglescreen", function (request, respond) {	
    // console.log(request.body.screen);
    let command = 'DisplaySwitch.exe /' + request.body.screen;
	exec(command, { stdio: 'inherit', encoding: 'utf-8' }, (error, stdout, stderr) => {
      if (error) {
        // console.log("error");
      } else {
        // console.log("no error");
        respond.sendStatus(200);
      }
    });
});

app.post("/startsession", function (request, respond) {  
    let sid = request.body.sid;
    let pid = request.body.pid;  
    if(sid!="" && pid!=""){
        CPid = pid;
        CSid = sid;
    }
});

app.post("/newsession", function (request, respond) {

    if(request.body.type!="") {
        CType = CTypes[request.body.type];
    }

    let uploadLocation = __dirname + '/LEARM-DATA/';
    uploadLocation += CPid + '_' + CSid;
    uploadLocation += '/session_data/';

    strFileName = uploadLocation + CPid + '_' + CSid + '_' + new Date().toISOString().slice(0,10) + '.csv';

    strFileName.split('/').slice(0,-1).reduce( (last, folder)=>{
        let folderPath = last ? (last + '/' + folder) : folder;
        if (!fs.existsSync(folderPath)) fs.mkdirSync(folderPath);
        return folderPath;
    })

    fs.open(strFileName, 'w' ,function (err, file) {
          if (err) throw err;
          console.log('New session file is created successfully.');
    });
    
    csvWriter = createCsvWriter({
      path: strFileName,
      header: [
        {id: 'pid', title: 'PId'},
        {id: 'type', title: 'Type'},
        {id: 'date', title: 'Date'},
        {id: 'delay', title: 'Delay'},
        {id: 'delaytype', title: 'Delay Type'},
        {id: 'cue', title: 'Cue'},
        {id: 'rate', title: 'Rate'},
        {id: 'review', title: 'Review'}
      ]
    });
});

function writeFileSyncRecursive(filename, content) {
    // create folder path if not exists
    filename.split('/').slice(0,-1).reduce( (last, folder)=>{
        let folderPath = last ? (last + '/' + folder) : folder;
        if (!fs.existsSync(folderPath)) fs.mkdirSync(folderPath);
        return folderPath;
    })
    
    fs.writeFileSync(filename, content);
}

app.post('/postMedia', upload.single('sessionBlob'), function (req, res) {
    let uploadLocation = __dirname + '/LEARM-DATA/';
    uploadLocation += CPid + '_' + CSid;
    uploadLocation += '/session_data/';

    if(req.file.originalname.indexOf("audio") >= 0){
        uploadLocation += 'tech_media/';
    }
    else {
        uploadLocation += 'subject_media/';
    }

    uploadLocation += req.file.originalname;

    writeFileSyncRecursive(uploadLocation, Buffer.from(new Uint8Array(req.file.buffer))); // write the blob to the server as a file
    res.sendStatus(200);
});

app.post('/postcue', function(request, respond) {
    // type, pid, date, version, delay, cue, rate, review  
    let date = new Date().toLocaleString("en-US");
    let delay = request.body.duration;
    let cue = request.body.cue;
    let rate = request.body.rate;
    let review = request.body.review;
    let delaytype = request.body.delaytype;

    const row = [ 
      {
        pid: CPid,
        type: CType,
        delaytype: delaytype,
        date: date,
        delay: delay,
        cue: cue,
        rate: rate,
        review: review
      }
    ];

    csvWriter
      .writeRecords(row)
      .then(()=> console.log('The CSV file was written successfully'));
});

app.listen(3000, function () {
    console.log("LEARM server started");
});