const express = require('express')
const crypto = require('crypto')
const session = require('express-session')
const PORT = process.env.PORT || 3000
const multer = require('multer')
const path = require('path')
const spawn = require('child_process').spawn;
const http = require('http');

const app = express()
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({limit: '50mb', extended: true}));

app.set("view engine", "ejs");
app.set('views',path.join(__dirname,'views'));
app.use('/static', express.static('static'))

function timeoutDestroy(req,res){
    console.log('Session destroyed')
    req.session.destroy((err)=>{
        res.redirect('index') ;
    })
    // http.get('http://localhost:3000/logout');
}

app.use(session({ 
    secret:'my secret key',
    resave:false,
    saveUninitialized: true,
    cookie: { secure: false }
}));

app.get('/index', (req, res) => {
    res.render('index')
});

app.get('/test',(req,res)=>{
    res.render('options');
});

app.get('/generate',(req,res)=>{
    console.log('received')
    const password = crypto.randomBytes(4).toString('HEX');
    req.session.password = password;
    req.session.timestamp = new Date().getTime(); 
    console.log(req.session.timestamp) ;
    res.render('options')
});

app.get('/cryptfile',(req,res)=>{
    res.render('cryptfile');
});

app.get('/crypttext',(req,res)=>{
    console.log('text') ;
    res.render('crypttext');
});

app.post('/validate',(req,res)=>{
    const {password} = req.body;
    if(req.session.password === password){
        return res.status(200).json({message:'Password is valid'});
    }
    return res.status(400).json({message:'Password is invalid'});
}); 

app.get('/timedout',(req,res)=>{
    console.log('timedout')
    res.render('timedout') ;
});

app.post('/data',(req,res)=>{

    const data = req.body;
    const password = req.session.password;
    const currentTime = new Date().getTime() ;
    const expirationTime = req.session.timestamp + 1000 * 30; // 2 minutes
    
    if(data && password && currentTime < expirationTime){
        req.session.password = null;
        req.session.timestamp = null;
        // Destroy the session and clear all session data
        req.session.destroy((err) => {
            if (err) {
            console.error('Error destroying session:', err);
            } else {
            console.log('Session destroyed successfully.');
            }
        });

        console.log(JSON.stringify(data)) ;
        // const pythonProcess = spawn('python',["./script.py", JSON.stringify(data), password]);
        return res.json({success:'true'});
    }
    else
    {
        res.status(400).json({error:'Invalid request'});
    }
})

app.post('/test',(req,res)=>{
    console.log("krupal") ;
    res.json(req.body);
    const data = req.body;
    console.log(data) ;
    // res.render('test',{data})
}) ;



app.post('/uploadText', (req, res) => {
    // console.log(req)
    // const password = req.session.password ;
    if(new Date().getTime() > (req.session.timestamp + 1000 * 60 * 2) || req.session.timestamp == null){
        console.log("out")
        req.session.timestamp = null ;
        req.session.destroy() ;
        res.redirect('timedout') ;
    }
    else
    {
        // console.log(req.body)
        const arg1 = req.body.plaintext ;
        const arg2 = "text" ;
        req.session.timestamp = null ;

        // Run the Python script
        const pythonProcess = spawn('python', ['script.py', arg1, arg2]);

        // Listen for data events on the stdout stream
        pythonProcess.stdout.on('data', (data) => {
        const output = JSON.parse(data);
        console.log(`Python script output:`, output);
        });

        // Listen for data events on the stderr stream
        pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        });

        // Listen for the 'close' event, which will be emitted when the Python script exits
        pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
        });

        // Listen for the 'exit' event, which will be emitted when the Python script has finished executing
        pythonProcess.on('exit', (code) => {
        console.log(`Python script finished executing with code ${code}`);
        });

        res.render('success') ;
        // return res.json({success:'true'});
    }
});

module.exports = app;

app.listen(PORT,()=>{
    console.log('Server running on 3000');
});