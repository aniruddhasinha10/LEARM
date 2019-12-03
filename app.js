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
    // run a windows command for switching the screen mode
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

    // called after the first page when the type of session is selected
    if(request.body.type!="") {
        CType = CTypes[request.body.type];
    }

    let uploadLocation = __dirname + '/LEARM-DATA/';
    uploadLocation += CPid + '_' + CSid;
    uploadLocation += '/session_data/';

    // create folders for each type of media
    createMediaFolders(uploadLocation);

    // create csv file for saving cue data
    strFileName = uploadLocation + CPid + '_' + CSid + '_' + new Date().toISOString().slice(0,10) + '.csv';

    createFolder(strFileName);

    fs.open(strFileName, 'w' ,function (err, file) {
          if (err) throw err;
          console.log('New session file is created successfully.');
    });
    
    // creating csv object , define colums/headers for the cue data
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
        {id: 'review', title: 'Review'},
        {id: 'isvideo', title: 'Video'},
        {id: 'videotype', title: 'Video Type'}
      ]
    });
});

function createMediaFolders(uploadLocation) {
    // audio & video folder creation for both technician and subject
    // subject_media, tech_media
    let subject_media = uploadLocation + 'subject_media/';
    let tech_media = uploadLocation + 'tech_media/';

    createFolder(subject_media + 'audio/');
    createFolder(subject_media + 'video/');
    createFolder(tech_media + 'audio/');
    createFolder(tech_media + 'video/');   
}

function createFolder(strFileName) {
    strFileName.split('/').slice(0,-1).reduce( (last, folder)=>{
        let folderPath = last ? (last + '/' + folder) : folder;
        if (!fs.existsSync(folderPath)) fs.mkdirSync(folderPath);
        return folderPath;
    })
}

function writeFileSyncRecursive(filename, content) {
    // create folder path if not exists
    createFolder(filename);
    
    fs.writeFileSync(filename, content);
}

app.post('/postMedia', upload.single('sessionBlob'), function (req, res) {
    
    // save video/audio files sent from learm client

    let uploadLocation = __dirname + '/LEARM-DATA/';
    uploadLocation += CPid + '_' + CSid;
    uploadLocation += '/session_data/';

    if(req.file.originalname.indexOf("audio") >= 0){
        uploadLocation += 'tech_media/audio/';
    }
    else {
        uploadLocation += 'subject_media/video/';
    }

    uploadLocation += req.file.originalname;

    // write the blob to the server as a file
    fs.writeFileSync(uploadLocation, Buffer.from(new Uint8Array(req.file.buffer)));
     
    res.sendStatus(200);
});

app.post('/postcue', function(request, respond) {
    // type, pid, date, version, delay, cue, rate, review  
    // get parameters from the call to save it in the csv file
    let date = new Date().toLocaleString("en-US");
    let delay = request.body.duration;
    let cue = request.body.cue;
    let rate = request.body.rate;
    let review = request.body.review;
    let delaytype = request.body.delaytype;
    let isvideo = request.body.isVideo ? request.body.isVideo : 0;
    let videotype = request.body.VideoType ? request.body.VideoType : "";

    const row = [ 
      {
        pid: CPid,
        type: CType,
        delaytype: delaytype,
        date: date,
        delay: delay,
        cue: cue,
        rate: rate,
        review: review,
        isvideo: isvideo,
        videotype: videotype
      }
    ];

    // write the cue record to csv file
    csvWriter
      .writeRecords(row)
      .then(()=> console.log('The CSV file was written successfully'));
});

app.listen(3000, function () {
    console.log("LEARM server started");
});