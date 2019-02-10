#!/bin/bash

vision_path="/Users/carlosj/Documents/Maestria/Tesis 1/Vision/NEE_Experimenter/stanford-ner-2018-10-16/"
stanford_path="/Users/carlosj/Documents/Maestria/Tesis 1/Vision/NEE-MOTOR/stanford-corenlp-full-2018-10-05/"

cd "$stanford_path" &&
java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-spanish.properties -port 9000 -timeout 15000 &
java -mx2g -cp "$vision_path"stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier "$vision_path"nee-experiment-model.ser.gz -textFile -port 9191 -outputFormat inlineXML