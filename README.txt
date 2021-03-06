
AWS CONFIGURATION and SERVICES
1. API Gateway: Import api_swagger.json to create a REST API, add headers (Access-Control-Allow-Headers, Access-Control-Allow-Methods, Access-Control-Allow-Origin), enable CORS, and export sdk files. 

2. S3 Bucket: Configure a bucket called vaccinationservicebucket to host the frontend files. Source link: https://docs.aws.amazon.com/AmazonS3/latest/userguide/CustomErrorDocSupport.html

3. Lambda: Create lambda functions for backend

4. LEX (V1): Perform chat operation (text request from users and message response from LEX). 
 

AWS: awsconfig 
1. api_swagger.json
This json file was built by SwaggerEditor (editor.swagger.io), and was later used to create a new REST API on Amazon API Gateway.


FRONT-END: frontend
1. index.html
This is the home or default page of the website.

2. error.html:
This is the error document enabled for static website hosting on S3 bucket. 

3. index.css
This file describes how HTML elements in index.html should be displayed.

4. index.js
This file incorporates functions to perform chat operations and exports functions from SDK.

5. SDK folder
This folder is automatically generated by API gateway on Amazon Website Service (AWS). 


BACK-END: backend
1. chatOperation.py
This lambda function performs chat operation based on API specification in API gateway. 

2. lexInvocation.py
This lambda function copied helper functions from orderFlower blueprint, which is an open-source on AWS official website. Source Link: https://docs.aws.amazon.com/lex/latest/dg/gs-bp.html
For subjective usage, task-driven functions are also included.  

3. dataScraper.py
This lambda function scrapes data from https://data.cityofnewyork.us/resource/w9ei-idxz.json and then stores data in DynamoDB, which is a noSQL service on AWS



