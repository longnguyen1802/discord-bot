# COMP4651 Chat Bot

## Abstract

This project presents the implementation of a serverless chatbot for image moderation, using OpenFaaS and Kubernetes. The chatbot employs multiple serverless functions to handle various tasks, such as image moderation, toxic comments moderation, chat and image generation functionalities.

## Background

OpenFaaS (Functions as a Service) is an open-source framework for building serverless functions using Docker containers. It provides a simple and flexible way to deploy and scale serverless functions, enabling developers to focus on the logic of their functions instead of the infrastructure. Kubernetes is a popular container orchestration platform that provides automated deployment, scaling, and management of containerized applications.

## System Design

The discord bot is implemented and deployed in an EC2 instance on AWS. The bot will listen to any incoming traffic in the discord channel and send the message to the OpenFaaS gateway. The OpenFaaS API Gateway routes each request to the appropriate function call. The OpenFaaS deployment is configured with a specified number of replicas, each representing an instance of the function that can handle incoming requests. When a request is received, the OpenFaaS gateway service routes the request to one of the running replicas. If the incoming request load exceeds the capacity of the running replicas, OpenFaaS can automatically scale up the deployment by creating additional replicas, using Kubernetes Horizontal Pod Autoscaler (HPA) to monitor the CPU usage of the replicas and adjust the number of replicas based on the defined scaling rules.

## Features

The chat bot is able to do the following tasks:

1. Image moderation
2. Text moderation
3. Image generation based on input prompt
4. Chat with user

### Image Moderation

The image moderation task utilizes a pre-trained Convolutional Neural Network (CNN) model to classify images as Safe for Work (SFW) or Not Safe for Work (NSFW). The script takes a URL of an image as input and uses the urllib2 library to download the image. It then uses the caffe library to preprocess and classify the image using the NSFW CNN model. The output of the classification is a dictionary containing the SFW and NSFW scores of the image. If the image download fails or there is an error during classification, the script outputs an error message. The code uses functions to organize the classification logic, including a function to create a transformer for the preprocessing of the image, a function to classify an image from a URL, and a main function that runs the script. The code also includes commands to disable and enable standard output for classification. The script can be run from the command line by passing a URL as an argument.

### Text Moderation

#### Back ground of Bert model

BERT, short for Bidirectional Encoder Representations from Transformers, is a Machine Learning (ML) model for natural language processing. It was developed in 2018 by researchers at Google AI Language and serves as a swiss army knife solution to 11+ of the most common language tasks, such as sentiment analysis and named entity recognition

#### Toxic comment model

The toxic comment model that we use is an finetuned version of bert model classify toxic comment.
It take advantage of transfer learning to use the pretrain bert model and finetune with the data from Kaggle Competition https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification/data

### Image Generation

The image generation task uses the OpenAI API to generate images based on an input prompt. DALL·E model is used in the image generation task. The discord bot listen to any incoming slash commands with the prefix as `/image` and `prompt` as the input. It then pass the `prompt` to the OpenFaas serverless function through the OpenFaas gateway. The serverless calls the OpenAI API to generate the image and do any necessary post-processing if any. The serverless function then return the generated image after processing to the discord bot and the bot will send the image to the discord channel.

Example use case: `/image prompt: a cat sitting on a chair`

### Chat

The chat task uses the OpenAI API to generate text based on the most recent 20 chat history with the user in the channel. GPT3.5-turbo model is used for this task.The discord bot listen to any incoming chat with the prefix as `!chat`. It then passes 100 messages to the OpenFaas serverless function through the OpenFaas gateway. The serverless function filters out only the top 20 chat history belonging to the bot or the user. OpenAI API is then called to generate the text response and do any necessary post-processing if any. The serverless function then return the generated text after processing to the discord bot and the bot will send the text to the discord channel.
