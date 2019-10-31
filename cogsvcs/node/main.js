'use strict';

// Node.js program to invoke Azure Cognitive Services and Text Translation.
// Chris Joakim, Microsoft, 2019/03/01
//
// Example command-line use:
// $ node main.js translate_doc Dire-Straits_Industrial-Disease 2 de
// $ node main.js translate_audio audio/can-you-keep-a-secret.wav
// $ node main.js translate_audio audio/ive-been-doing-a-lot-of-thinking.wav
// $ node main.js translate_audio audio/can-you-keep-a-secret.wav
// $ node main.js translate_audio audio/gettysburg10.wav

const fs = require('fs');
const os = require('os');
const util = require('util');
const request = require('request');
const uuidv4  = require('uuid/v4');
const csssdk = require("microsoft-cognitiveservices-speech-sdk");

const cogsvcs_name      = process.env.AZURE_COGSVCS_NAME;
const cogsvcs_key       = process.env.AZURE_COGSVCS_KEY;
const speech_name       = process.env.AZURE_SPEECH_NAME;
const speech_key        = process.env.AZURE_SPEECH_KEY;
const texttrans_name    = process.env.AZURE_TEXTTRANS_NAME;
const texttrans_key     = process.env.AZURE_TEXTTRANS_KEY;
const texttrans_baseurl = process.env.AZURE_TEXTTRANS_BASEURL;

if (!texttrans_name) {
    throw new Error('Environment variable AZURE_TEXTTRANS_NAME is not set.')
};
if (!texttrans_key) {
    throw new Error('Environment variable AZURE_TEXTTRANS_KEY is not set.')
};
if (!texttrans_baseurl) {
    throw new Error('Environment variable AZURE_TEXTTRANS_BASEURL is not set.')
};


class Main {

    constructor() {

    }

    execute() {

        if (process.argv.length < 3) {
            console.log('error: too few command-line args provided.');
            process.exit();
        }
        else {
            var funct = process.argv[2];

            switch (funct) {

                case 'translate_doc':
                    var songname  = process.argv[3];
                    var num_lines = parseInt(process.argv[4]); 
                    var to_lang   = process.argv[5];
                    this.translate_doc(songname, num_lines, to_lang);
                    break;

                case 'translate_audio':
                    var infile  = process.argv[3];
                    this.translate_audio(infile);
                    break;

                default:
                    console.log('error: unknown function - ' + funct);
            }
        }
    }

    translate_doc(songname, num_lines, to_lang) {
        console.log('function: translate_doc ' + songname + ' -> ' + to_lang + ' ' + num_lines);
        var infile  = 'data/' + songname + '.json';
        var outfile = 'tmp/' + songname + '_tmp_' + to_lang + '.json';
        
        // Read the input file in the data/ directory
        var jstr = fs.readFileSync(infile, 'utf8');
        var song = JSON.parse(jstr);
        var original_lines = song['text_lines'];
        var subset_lines = [];

        for (var i = 0; i < num_lines; i++) {
            console.log('' + i);
            if (original_lines.length > i) {
                subset_lines.push(original_lines[i]);
            }
        }
        console.log(subset_lines);
        var source_text = subset_lines.join(" ");

        var request_options = this.txt_tran_request_options(source_text, to_lang);
        console.log("request options:\n" + JSON.stringify(request_options, null, 2));
        this.execute_tran_http_request(request_options, source_text, outfile);
    }

    txt_tran_request_options(source_text, to_lang) {
        var options = {};
        options['method'] = 'POST';
        options['baseUrl'] = 'https://api.cognitive.microsofttranslator.com/';
        options['url'] = 'translate';
        options['qs']  = this.txt_tran_qs(to_lang);
        options['headers'] = this.txt_tran_headers();
        options['body'] = this.txt_tran_body(source_text); 
        options['json'] = true;
        return options;
    }

    txt_tran_headers() {
        var headers = {};
        headers['Ocp-Apim-Subscription-Key'] = texttrans_key;
        headers['Content-type'] = 'application/json';
        headers['X-ClientTraceId'] = uuidv4().toString();
        return headers;
    }

    txt_tran_qs(to_lang) {
        var obj = {};
        obj['api-version'] = '3.0';
        obj['to'] = to_lang;
        return obj;
    }

    txt_tran_body(source_text) {
        // return an array with an object like this: [{'text': 'Hello World'}];
        var obj = {};
        obj['text'] = source_text;
        return [obj]; 
    }

    execute_tran_http_request(request_options, source_text, outfile) {
        // Use the npm 'request' library to execute the actual HTTP calls
        // See https://www.npmjs.com/package/request

        console.log("request options:\n" + JSON.stringify(request_options, null, 2));

        request(request_options, function(err, res, body) { 
            console.log('---');
            if (err) {
                console.log('response error: ' + err); 
            }
            else {
                console.log('response status code: ' + res.statusCode);
                body[0]['source_text'] = source_text;
                var jstr = JSON.stringify(body, null, 2);
                console.log(jstr);
                fs.writeFileSync(outfile, jstr);
                console.log('file written: ' + outfile);
            }
        });
    }

    translate_audio(infile) {
        // See https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstart-js-node

        console.log('function: translate_audio: ' + infile);
        var region = 'eastus';

        // create the push stream we need for the speech sdk.
        var pushStream = csssdk.AudioInputStream.createPushStream();

        // open the file and push it to the push stream.
        fs.createReadStream(infile).on('data', function(arrayBuffer) {
            pushStream.write(arrayBuffer.buffer);
        }).on('end', function() {
            pushStream.close();
        });

        // we are done with the setup
        console.log("Now recognizing from: " + infile);

        // now create the audio-config pointing to our stream and
        // the speech config specifying the language.
        var audioConfig = csssdk.AudioConfig.fromStreamInput(pushStream);
        var speechConfig = csssdk.SpeechConfig.fromSubscription(speech_key, region);

        // setting the recognition language to English.
        speechConfig.speechRecognitionLanguage = "en-US";

        // create the speech recognizer.
        var recognizer = new csssdk.SpeechRecognizer(speechConfig, audioConfig);

        // start the recognizer and wait for a result.
        recognizer.recognizeOnceAsync(
            function (result) {
                console.log(result);
                recognizer.close();
                recognizer = undefined;
            },
            function (err) {
                console.trace("err - " + err);
                recognizer.close();
                recognizer = undefined;
            }
        );
    }
}

new Main().execute();
